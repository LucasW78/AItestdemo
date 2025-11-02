"""
Document model for storing file information.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, Text, Boolean
from sqlalchemy.orm import relationship

from app.database import Base


class Document(Base):
    """
    Document model representing uploaded files.
    """
    __tablename__ = "documents"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    file_type = Column(String, nullable=False)
    mime_type = Column(String, nullable=False)

    # Processing status
    processed = Column(Boolean, default=False)
    processing_status = Column(String, default="pending")  # pending, processing, completed, failed
    processing_error = Column(Text, nullable=True)

    # Extracted content
    extracted_text = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    test_cases = relationship("TestCase", back_populates="document")

    def __repr__(self):
        return f"<Document(id={self.id}, filename={self.filename})>"