"""
RAG (Retrieval-Augmented Generation) pipeline implementation.
"""
import logging
import uuid
import asyncio
from typing import List, Dict, Any, Optional, Tuple
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

from app.config import settings
from app.core.ocr_processor import OCRProcessor

logger = logging.getLogger(__name__)


class RAGPipeline:
    """
    RAG pipeline for document indexing and retrieval.
    """

    def __init__(self):
        """Initialize RAG pipeline with ChromaDB and embedding model."""
        # Initialize ChromaDB client
        try:
            if settings.chroma_db_path.startswith('http'):
                # Remote ChromaDB
                self.chroma_client = chromadb.HttpClient(
                    host=settings.chroma_db_path.split(':')[0],
                    port=settings.chroma_db_path.split(':')[1] if ':' in settings.chroma_db_path else 8000
                )
            else:
                # Local ChromaDB
                self.chroma_client = chromadb.PersistentClient(
                    path=settings.chroma_db_path
                )

            # Get or create collection
            self.collection = self.chroma_client.get_or_create_collection(
                name=settings.chroma_collection_name,
                metadata={"hnsw:space": "cosine"}
            )

            logger.info(f"ChromaDB initialized with collection: {settings.chroma_collection_name}")

        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            raise

        # Initialize embedding model
        try:
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("SentenceTransformer model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise

        # Initialize OCR processor
        self.ocr_processor = OCRProcessor()

        # Text chunking parameters
        self.chunk_size = 500  # characters
        self.chunk_overlap = 50  # characters

    async def index_document(self, document_id: str, text: str, metadata: Optional[Dict] = None) -> bool:
        """
        Index a document in the RAG system.

        Args:
            document_id: Unique document identifier
            text: Text content to index
            metadata: Additional metadata for the document

        Returns:
            True if indexing was successful, False otherwise
        """
        try:
            logger.info(f"Starting document indexing for: {document_id}")

            # Split text into chunks
            chunks = self._split_text(text)

            if not chunks:
                logger.warning(f"No chunks created for document: {document_id}")
                return False

            logger.info(f"Created {len(chunks)} chunks for document: {document_id}")

            # Generate embeddings for all chunks
            embeddings = self.embedding_model.encode(
                chunks,
                convert_to_tensor=True,
                show_progress_bar=True
            )

            # Prepare documents for ChromaDB
            documents = []
            metadatas = []
            ids = []

            for i, chunk in enumerate(chunks):
                chunk_id = f"{document_id}_chunk_{i}"
                documents.append(chunk)
                ids.append(chunk_id)

                # Prepare metadata
                chunk_metadata = {
                    "document_id": document_id,
                    "chunk_index": i,
                    "chunk_text": chunk[:100] + "..." if len(chunk) > 100 else chunk,
                    **(metadata or {})
                }
                metadatas.append(chunk_metadata)

            # Add to ChromaDB
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids,
                embeddings=embeddings.tolist()
            )

            logger.info(f"Successfully indexed document: {document_id}")
            return True

        except Exception as e:
            logger.error(f"Error indexing document {document_id}: {e}")
            return False

    async def remove_document(self, document_id: str) -> bool:
        """
        Remove a document from the RAG system.

        Args:
            document_id: Document identifier to remove

        Returns:
            True if removal was successful, False otherwise
        """
        try:
            # Get all document chunks
            results = self.collection.get(
                where={"document_id": document_id}
            )

            if results['ids']:
                # Delete all chunks for this document
                self.collection.delete(ids=results['ids'])
                logger.info(f"Removed {len(results['ids'])} chunks for document: {document_id}")
                return True
            else:
                logger.warning(f"No chunks found for document: {document_id}")
                return False

        except Exception as e:
            logger.error(f"Error removing document {document_id}: {e}")
            return False

    async def query(
        self,
        query_text: str,
        n_results: int = 5,
        document_ids: Optional[List[str]] = None,
        min_confidence: float = 0.5
    ) -> Dict[str, Any]:
        """
        Query the RAG system for relevant documents.

        Args:
            query_text: Query text
            n_results: Number of results to return
            document_ids: Optional list of document IDs to search within
            min_confidence: Minimum confidence threshold for results

        Returns:
            Dictionary containing query results and metadata
        """
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query_text])

            # Prepare where clause if document IDs are specified
            where_clause = None
            if document_ids:
                where_clause = {"document_id": {"$in": document_ids}}

            # Query ChromaDB
            results = self.collection.query(
                query_embeddings=query_embedding.tolist(),
                n_results=n_results,
                where=where_clause,
                include=["documents", "metadatas", "distances"]
            )

            # Process results
            processed_results = []
            for i in range(len(results['ids'][0])):
                doc_id = results['ids'][0][i]
                document = results['documents'][0][i]
                metadata = results['metadatas'][0][i]
                distance = results['distances'][0][i]

                # Convert distance to confidence score (cosine similarity)
                confidence = 1 - distance

                # Filter by minimum confidence
                if confidence >= min_confidence:
                    processed_results.append({
                        "id": doc_id,
                        "document": document,
                        "metadata": metadata,
                        "confidence": confidence,
                        "distance": distance
                    })

            # Sort by confidence (highest first)
            processed_results.sort(key=lambda x: x['confidence'], reverse=True)

            return {
                "query": query_text,
                "results": processed_results,
                "total_found": len(processed_results),
                "searched_documents": len(document_ids) if document_ids else None
            }

        except Exception as e:
            logger.error(f"Error querying RAG system: {e}")
            return {
                "query": query_text,
                "results": [],
                "total_found": 0,
                "error": str(e)
            }

    async def get_document_chunks(self, document_id: str) -> List[Dict[str, Any]]:
        """
        Get all chunks for a specific document.

        Args:
            document_id: Document identifier

        Returns:
            List of document chunks
        """
        try:
            results = self.collection.get(
                where={"document_id": document_id},
                include=["documents", "metadatas"]
            )

            chunks = []
            for i in range(len(results['ids'])):
                chunks.append({
                    "id": results['ids'][i],
                    "document": results['documents'][i],
                    "metadata": results['metadatas'][i]
                })

            # Sort by chunk index
            chunks.sort(key=lambda x: x['metadata']['chunk_index'])

            return chunks

        except Exception as e:
            logger.error(f"Error getting document chunks for {document_id}: {e}")
            return []

    async def hybrid_search(
        self,
        query_text: str,
        n_results: int = 5,
        document_ids: Optional[List[str]] = None,
        keyword_weight: float = 0.3,
        semantic_weight: float = 0.7
    ) -> Dict[str, Any]:
        """
        Perform hybrid search combining keyword and semantic search.

        Args:
            query_text: Query text
            n_results: Number of results to return
            document_ids: Optional list of document IDs to search within
            keyword_weight: Weight for keyword matching (0-1)
            semantic_weight: Weight for semantic similarity (0-1)

        Returns:
            Dictionary containing hybrid search results
        """
        try:
            # Semantic search
            semantic_results = await self.query(
                query_text=query_text,
                n_results=n_results * 2,  # Get more semantic results
                document_ids=document_ids
            )

            # Keyword search (simple implementation)
            keyword_results = await self._keyword_search(
                query_text=query_text,
                n_results=n_results * 2,
                document_ids=document_ids
            )

            # Combine results
            combined_results = self._combine_search_results(
                semantic_results['results'],
                keyword_results,
                keyword_weight,
                semantic_weight
            )

            # Take top n_results
            final_results = combined_results[:n_results]

            return {
                "query": query_text,
                "results": final_results,
                "total_found": len(final_results),
                "semantic_count": len(semantic_results['results']),
                "keyword_count": len(keyword_results)
            }

        except Exception as e:
            logger.error(f"Error in hybrid search: {e}")
            return {
                "query": query_text,
                "results": [],
                "total_found": 0,
                "error": str(e)
            }

    def _split_text(self, text: str) -> List[str]:
        """
        Split text into chunks for processing.

        Args:
            text: Text to split

        Returns:
            List of text chunks
        """
        if not text:
            return []

        # Simple text chunking - can be enhanced with more sophisticated methods
        chunks = []
        start = 0
        text_length = len(text)

        while start < text_length:
            end = start + self.chunk_size

            # Try to break at sentence or paragraph boundaries
            if end < text_length:
                # Look for sentence endings
                sentence_endings = ['.', '!', '?', '。', '！', '？']
                for i in range(end, max(start, end - 100), -1):
                    if text[i] in sentence_endings and i + 1 < text_length:
                        end = i + 1
                        break
                else:
                    # Look for word boundaries
                    for i in range(end, max(start, end - 50), -1):
                        if text[i] == ' ' or text[i] == '\n':
                            end = i
                            break

            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            start = end - self.chunk_overlap if end < text_length else end

        return chunks

    async def _keyword_search(
        self,
        query_text: str,
        n_results: int = 5,
        document_ids: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Simple keyword-based search.

        Args:
            query_text: Query text
            n_results: Number of results to return
            document_ids: Optional list of document IDs to search within

        Returns:
            List of keyword search results
        """
        try:
            # Get all documents (or filter by document_ids)
            where_clause = None
            if document_ids:
                where_clause = {"document_id": {"$in": document_ids}}

            all_docs = self.collection.get(
                where=where_clause,
                include=["documents", "metadatas"]
            )

            # Simple keyword matching
            query_terms = query_text.lower().split()
            results = []

            for i, doc in enumerate(all_docs['documents']):
                doc_lower = doc.lower()
                score = 0

                # Count term matches
                for term in query_terms:
                    if term in doc_lower:
                        score += doc_lower.count(term)

                if score > 0:
                    results.append({
                        "id": all_docs['ids'][i],
                        "document": doc,
                        "metadata": all_docs['metadatas'][i],
                        "confidence": min(score / len(query_terms), 1.0),
                        "score": score
                    })

            # Sort by score and return top results
            results.sort(key=lambda x: x['score'], reverse=True)
            return results[:n_results]

        except Exception as e:
            logger.error(f"Error in keyword search: {e}")
            return []

    def _combine_search_results(
        self,
        semantic_results: List[Dict],
        keyword_results: List[Dict],
        keyword_weight: float,
        semantic_weight: float
    ) -> List[Dict[str, Any]]:
        """
        Combine semantic and keyword search results.

        Args:
            semantic_results: Results from semantic search
            keyword_results: Results from keyword search
            keyword_weight: Weight for keyword results
            semantic_weight: Weight for semantic results

        Returns:
            Combined and sorted results
        """
        # Normalize weights
        total_weight = keyword_weight + semantic_weight
        keyword_weight /= total_weight
        semantic_weight /= total_weight

        # Create result map
        result_map = {}

        # Process semantic results
        for result in semantic_results:
            doc_id = result['id']
            result_map[doc_id] = {
                **result,
                'semantic_confidence': result['confidence'],
                'keyword_confidence': 0.0,
                'combined_confidence': result['confidence'] * semantic_weight
            }

        # Process keyword results and combine
        for result in keyword_results:
            doc_id = result['id']
            if doc_id in result_map:
                # Combine scores
                existing = result_map[doc_id]
                existing['keyword_confidence'] = result['confidence']
                existing['combined_confidence'] = (
                    existing['semantic_confidence'] * semantic_weight +
                    result['confidence'] * keyword_weight
                )
            else:
                # Add keyword-only result
                result_map[doc_id] = {
                    **result,
                    'semantic_confidence': 0.0,
                    'keyword_confidence': result['confidence'],
                    'combined_confidence': result['confidence'] * keyword_weight
                }

        # Sort by combined confidence
        combined_results = list(result_map.values())
        combined_results.sort(key=lambda x: x['combined_confidence'], reverse=True)

        return combined_results

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the RAG system.

        Returns:
            Dictionary containing system statistics
        """
        try:
            count = self.collection.count()
            return {
                "total_chunks": count,
                "collection_name": settings.chroma_collection_name,
                "embedding_model": "all-MiniLM-L6-v2",
                "chunk_size": self.chunk_size,
                "chunk_overlap": self.chunk_overlap
            }
        except Exception as e:
            logger.error(f"Error getting RAG stats: {e}")
            return {"error": str(e)}