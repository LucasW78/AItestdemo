"""
Document service for handling document operations.
"""
import os
import uuid
import logging
from typing import List, Tuple, Optional
from fastapi import UploadFile
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.config import settings
from app.schemas.document import DocumentCreate, DocumentUpdate
from app.models.document import Document as DocumentModel
from app.core.file_processor import FileProcessor

logger = logging.getLogger(__name__)


class DocumentService:
    """
    Service for document management operations.
    """

    def __init__(self, db: Session):
        self.db = db
        self.upload_dir = settings.upload_dir

    async def create_document(
        self,
        document_data: DocumentCreate,
        file: Optional[UploadFile] = None
    ) -> DocumentModel:
        """
        Create a new document record.
        """
        try:
            # Validate file before processing
            if file:
                is_valid, message = FileProcessor.validate_file(
                    file.filename,
                    file.size
                )
                if not is_valid:
                    raise ValueError(message)

            # Generate unique ID and filename
            document_id = str(uuid.uuid4())
            file_extension = document_data.file_type
            unique_filename = f"{document_id}.{file_extension}"
            file_path = os.path.join(self.upload_dir, unique_filename)

            # Save file if provided
            file_content = None
            if file:
                os.makedirs(self.upload_dir, exist_ok=True)
                file_content = await file.read()
                with open(file_path, "wb") as buffer:
                    buffer.write(file_content)

            # Create document record
            db_document = DocumentModel(
                id=document_id,
                filename=unique_filename,
                original_filename=document_data.original_filename,
                file_path=file_path,
                file_size=document_data.file_size,
                file_type=document_data.file_type,
                mime_type=document_data.mime_type,
                processing_status="uploaded"
            )

            self.db.add(db_document)
            self.db.commit()
            self.db.refresh(db_document)

            logger.info(f"Document created: {document_id}")
            return db_document

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating document: {e}")
            raise

    async def get_document(self, document_id: str) -> Optional[DocumentModel]:
        """
        Get a document by ID.
        """
        try:
            document = self.db.query(DocumentModel).filter(
                DocumentModel.id == document_id
            ).first()
            return document

        except Exception as e:
            logger.error(f"Error retrieving document {document_id}: {e}")
            raise

    async def list_documents(
        self,
        page: int = 1,
        per_page: int = 20,
        status: Optional[str] = None,
        file_type: Optional[str] = None
    ) -> Tuple[List[DocumentModel], int]:
        """
        List documents with pagination and filtering.
        """
        try:
            query = self.db.query(DocumentModel)

            # Apply filters
            if status:
                query = query.filter(DocumentModel.processing_status == status)
            if file_type:
                query = query.filter(DocumentModel.file_type == file_type)

            # Count total records
            total = query.count()

            # Apply pagination
            offset = (page - 1) * per_page
            documents = query.order_by(desc(DocumentModel.created_at)).offset(
                offset
            ).limit(per_page).all()

            return documents, total

        except Exception as e:
            logger.error(f"Error listing documents: {e}")
            raise

    async def update_document(
        self,
        document_id: str,
        document_update: DocumentUpdate
    ) -> Optional[DocumentModel]:
        """
        Update a document.
        """
        try:
            document = self.db.query(DocumentModel).filter(
                DocumentModel.id == document_id
            ).first()

            if not document:
                return None

            # Update fields
            update_data = document_update.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(document, field, value)

            self.db.commit()
            self.db.refresh(document)

            logger.info(f"Document updated: {document_id}")
            return document

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating document {document_id}: {e}")
            raise

    async def delete_document(self, document_id: str) -> bool:
        """
        Delete a document.
        """
        try:
            document = self.db.query(DocumentModel).filter(
                DocumentModel.id == document_id
            ).first()

            if not document:
                return False

            # Delete file from disk
            if os.path.exists(document.file_path):
                os.remove(document.file_path)

            # Delete database record
            self.db.delete(document)
            self.db.commit()

            logger.info(f"Document deleted: {document_id}")
            return True

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting document {document_id}: {e}")
            raise

    async def process_document(self, document_id: str) -> None:
        """
        Process a document for RAG indexing.
        """
        try:
            document = await self.get_document(document_id)
            if not document:
                raise ValueError(f"Document not found: {document_id}")

            # Update status to processing
            await self.update_document(
                document_id,
                DocumentUpdate(processing_status="processing")
            )

            # Extract text from document
            extracted_text = await FileProcessor.extract_text(
                document.file_path,
                document.file_type
            )

            if not extracted_text or not extracted_text.strip():
                raise ValueError("No text could be extracted from the document")

            # Update document with extracted text
            await self.update_document(
                document_id,
                DocumentUpdate(
                    processed=True,
                    processing_status="completed",
                    extracted_text=extracted_text
                )
            )

            logger.info(f"Document processed: {document_id}")

        except Exception as e:
            # Mark as failed
            await self.update_document(
                document_id,
                DocumentUpdate(
                    processing_status="failed",
                    processing_error=str(e)
                )
            )
            logger.error(f"Error processing document {document_id}: {e}")
            raise