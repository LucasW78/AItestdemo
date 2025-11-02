"""
Mind map model for storing test case visualizations.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.database import Base


class MindMap(Base):
    """
    Mind map model representing test case visualizations.
    """
    __tablename__ = "mind_maps"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    # Mind map data structure
    nodes = Column(JSON, nullable=False)  # Mind map nodes
    edges = Column(JSON, nullable=False)  # Connections between nodes
    layout = Column(JSON, nullable=True)  # Layout configuration

    # Associated test cases
    test_case_ids = Column(JSON, nullable=False)  # List of test case IDs

    # Generation metadata
    generation_config = Column(JSON, nullable=True)  # Configuration used for generation
    version = Column(Integer, default=1)

    # Status
    status = Column(String, default="active")  # active, archived

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships (virtual - not a real FK)
    test_cases = relationship("TestCase", secondary="mind_map_test_cases", back_populates="mind_maps")

    def __repr__(self):
        return f"<MindMap(id={self.id}, title={self.title})>"


# Association table for many-to-many relationship
class MindMapTestCase(Base):
    """
    Association table for MindMap and TestCase many-to-many relationship.
    """
    __tablename__ = "mind_map_test_cases"

    mind_map_id = Column(String, ForeignKey("mind_maps.id"), primary_key=True)
    test_case_id = Column(String, ForeignKey("test_cases.id"), primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)