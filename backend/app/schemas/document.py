"""
Pydantic schemas for Document operations.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class DocumentBase(BaseModel):
    """Base document schema."""
    filename: str = Field(..., description="Document filename")
    original_filename: str = Field(..., description="Original uploaded filename")
    file_type: str = Field(..., description="File extension")
    mime_type: str = Field(..., description="MIME type")


class DocumentCreate(DocumentBase):
    """Schema for creating documents."""
    file_path: str = Field(..., description="Path to stored file")
    file_size: int = Field(..., description="File size in bytes")


class DocumentUpdate(BaseModel):
    """Schema for updating documents."""
    processed: Optional[bool] = None
    processing_status: Optional[str] = None
    processing_error: Optional[str] = None
    extracted_text: Optional[str] = None


class DocumentInDB(DocumentBase):
    """Schema for documents in database."""
    id: str
    file_path: str
    file_size: int
    processed: bool
    processing_status: str
    processing_error: Optional[str]
    extracted_text: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Document(DocumentInDB):
    """Schema for document responses."""
    pass


class DocumentList(BaseModel):
    """Schema for document list responses."""
    documents: List[Document]
    total: int
    page: int
    per_page: int


class DocumentProcessingStatus(BaseModel):
    """Schema for document processing status."""
    document_id: str
    status: str
    error: Optional[str] = None
    progress: Optional[int] = None  # 0-100