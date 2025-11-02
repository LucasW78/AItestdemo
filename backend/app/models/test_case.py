"""
Test case model for storing AI-generated test cases.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.database import Base


class TestCase(Base):
    """
    Test case model representing AI-generated test cases.
    """
    __tablename__ = "test_cases"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    preconditions = Column(Text, nullable=True)
    steps = Column(JSON, nullable=True)  # List of test steps
    expected_result = Column(Text, nullable=True)
    priority = Column(String, default="medium")  # low, medium, high, critical
    category = Column(String, nullable=True)
    tags = Column(JSON, nullable=True)  # List of tags

    # Generation metadata
    document_id = Column(String, ForeignKey("documents.id"), nullable=False)
    generation_prompt = Column(Text, nullable=True)
    generation_context = Column(Text, nullable=True)

    # Status
    status = Column(String, default="draft")  # draft, approved, deprecated
    manual_review = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    document = relationship("Document", back_populates="test_cases")
    mind_maps = relationship("MindMap", back_populates="test_cases")

    def __repr__(self):
        return f"<TestCase(id={self.id}, title={self.title})>"