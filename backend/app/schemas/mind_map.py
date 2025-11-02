"""
Pydantic schemas for MindMap operations.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class MindMapNode(BaseModel):
    """Schema for mind map node."""
    id: str = Field(..., description="Node unique identifier")
    label: str = Field(..., description="Node text label")
    type: str = Field("default", description="Node type")
    x: Optional[float] = Field(None, description="Node X position")
    y: Optional[float] = Field(None, description="Node Y position")
    color: Optional[str] = Field(None, description="Node color")
    size: Optional[int] = Field(None, description="Node size")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional node data")
    parent_id: Optional[str] = Field(None, description="Parent node ID")


class MindMapEdge(BaseModel):
    """Schema for mind map edge/connection."""
    id: str = Field(..., description="Edge unique identifier")
    source: str = Field(..., description="Source node ID")
    target: str = Field(..., description="Target node ID")
    label: Optional[str] = Field(None, description="Edge label")
    color: Optional[str] = Field(None, description="Edge color")
    width: Optional[int] = Field(None, description="Edge width")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional edge data")


class MindMapLayout(BaseModel):
    """Schema for mind map layout configuration."""
    algorithm: str = Field("hierarchical", description="Layout algorithm")
    direction: str = Field("TB", description="Layout direction (TB, BT, LR, RL)")
    node_spacing: float = Field(100, description="Spacing between nodes")
    level_spacing: float = Field(150, description="Spacing between levels")


class MindMapBase(BaseModel):
    """Base mind map schema."""
    title: str = Field(..., description="Mind map title")
    description: Optional[str] = Field(None, description="Mind map description")
    layout: Optional[MindMapLayout] = Field(None, description="Layout configuration")


class MindMapCreate(MindMapBase):
    """Schema for creating mind maps."""
    nodes: List[MindMapNode] = Field(..., description="Mind map nodes")
    edges: List[MindMapEdge] = Field(..., description="Mind map edges")
    test_case_ids: List[str] = Field(..., description="Associated test case IDs")
    generation_config: Optional[Dict[str, Any]] = Field(None, description="Generation configuration")


class MindMapUpdate(BaseModel):
    """Schema for updating mind maps."""
    title: Optional[str] = None
    description: Optional[str] = None
    nodes: Optional[List[MindMapNode]] = None
    edges: Optional[List[MindMapEdge]] = None
    layout: Optional[MindMapLayout] = None
    status: Optional[str] = None


class MindMapInDB(MindMapBase):
    """Schema for mind maps in database."""
    id: str
    nodes: List[Dict[str, Any]]  # JSON stored in DB
    edges: List[Dict[str, Any]]  # JSON stored in DB
    test_case_ids: List[str]
    generation_config: Optional[Dict[str, Any]]
    version: int
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MindMap(MindMapInDB):
    """Schema for mind map responses."""
    pass


class MindMapList(BaseModel):
    """Schema for mind map list responses."""
    mind_maps: List[MindMap]
    total: int
    page: int
    per_page: int


class MindMapGeneration(BaseModel):
    """Schema for mind map generation requests."""
    test_case_ids: List[str] = Field(..., description="Source test case IDs")
    title: Optional[str] = Field(None, description="Mind map title")
    layout: Optional[MindMapLayout] = Field(None, description="Layout configuration")
    group_by: Optional[str] = Field("category", description="Grouping strategy")
    max_depth: Optional[int] = Field(3, description="Maximum depth of mind map")


class MindMapGenerationResponse(BaseModel):
    """Schema for mind map generation responses."""
    task_id: str
    status: str
    message: str