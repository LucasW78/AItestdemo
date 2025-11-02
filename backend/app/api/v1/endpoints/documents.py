"""
Document management API endpoints.
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_database
from app.schemas.document import (
    Document, DocumentList, DocumentProcessingStatus,
    DocumentCreate, DocumentUpdate
)
from app.models.document import Document as DocumentModel
from app.services.document_service import DocumentService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/upload", response_model=Document, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_database)
):
    """
    Upload a new document.
    """
    # Validate file
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file provided"
        )

    # TODO: Implement file validation and processing
    document_service = DocumentService(db)

    try:
        # Create document record
        document_data = DocumentCreate(
            filename=f"{file.filename}_{file.size}",  # Temporary filename
            original_filename=file.filename,
            file_path="",  # Will be set after saving
            file_size=file.size,
            file_type=file.filename.split('.')[-1] if '.' in file.filename else '',
            mime_type=file.content_type or 'application/octet-stream'
        )

        document = await document_service.create_document(document_data, file)
        logger.info(f"Document uploaded successfully: {document.id}")
        return document

    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading document: {str(e)}"
        )


@router.get("/", response_model=DocumentList)
async def list_documents(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    file_type: Optional[str] = Query(None),
    db: Session = Depends(get_database)
):
    """
    List documents with pagination and filtering.
    """
    document_service = DocumentService(db)

    try:
        documents, total = await document_service.list_documents(
            page=page,
            per_page=per_page,
            status=status,
            file_type=file_type
        )

        return DocumentList(
            documents=documents,
            total=total,
            page=page,
            per_page=per_page
        )

    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving documents"
        )


@router.get("/{document_id}", response_model=Document)
async def get_document(
    document_id: str,
    db: Session = Depends(get_database)
):
    """
    Get a specific document by ID.
    """
    document_service = DocumentService(db)

    try:
        document = await document_service.get_document(document_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        return document

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving document {document_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving document"
        )


@router.put("/{document_id}", response_model=Document)
async def update_document(
    document_id: str,
    document_update: DocumentUpdate,
    db: Session = Depends(get_database)
):
    """
    Update a document.
    """
    document_service = DocumentService(db)

    try:
        document = await document_service.update_document(document_id, document_update)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        return document

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating document {document_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating document"
        )


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: str,
    db: Session = Depends(get_database)
):
    """
    Delete a document.
    """
    document_service = DocumentService(db)

    try:
        success = await document_service.delete_document(document_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document {document_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting document"
        )


@router.post("/{document_id}/process", response_model=DocumentProcessingStatus)
async def process_document(
    document_id: str,
    db: Session = Depends(get_database)
):
    """
    Process a document for RAG indexing.
    """
    document_service = DocumentService(db)

    try:
        # Check if document exists
        document = await document_service.get_document(document_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )

        # Start processing (async)
        await document_service.process_document(document_id)

        return DocumentProcessingStatus(
            document_id=document_id,
            status="processing",
            progress=0
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing document {document_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing document"
        )


@router.get("/{document_id}/status", response_model=DocumentProcessingStatus)
async def get_document_status(
    document_id: str,
    db: Session = Depends(get_database)
):
    """
    Get document processing status.
    """
    document_service = DocumentService(db)

    try:
        document = await document_service.get_document(document_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )

        progress = 100 if document.processed else 0

        return DocumentProcessingStatus(
            document_id=document_id,
            status=document.processing_status,
            error=document.processing_error,
            progress=progress
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document status {document_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving document status"
        )