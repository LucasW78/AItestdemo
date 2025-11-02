"""
Pydantic schemas for TestCase operations.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class TestCaseStep(BaseModel):
    """Schema for individual test case step."""
    step_number: int = Field(..., description="Step order number")
    action: str = Field(..., description="Action to perform")
    expected_result: str = Field(..., description="Expected result of this step")
    notes: Optional[str] = None


class TestCaseBase(BaseModel):
    """Base test case schema."""
    title: str = Field(..., description="Test case title")
    description: Optional[str] = Field(None, description="Test case description")
    preconditions: Optional[str] = Field(None, description="Test preconditions")
    expected_result: Optional[str] = Field(None, description="Overall expected result")
    priority: str = Field("medium", description="Test priority")
    category: Optional[str] = Field(None, description="Test category")
    tags: Optional[List[str]] = Field(None, description="Test tags")


class TestCaseCreate(TestCaseBase):
    """Schema for creating test cases."""
    steps: Optional[List[TestCaseStep]] = Field(None, description="Test steps")
    document_id: str = Field(..., description="Source document ID")
    generation_prompt: Optional[str] = Field(None, description="Prompt used for generation")
    generation_context: Optional[str] = Field(None, description="Context used for generation")


class TestCaseUpdate(BaseModel):
    """Schema for updating test cases."""
    title: Optional[str] = None
    description: Optional[str] = None
    preconditions: Optional[str] = None
    steps: Optional[List[TestCaseStep]] = None
    expected_result: Optional[str] = None
    priority: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    status: Optional[str] = None
    manual_review: Optional[str] = None


class TestCaseInDB(TestCaseBase):
    """Schema for test cases in database."""
    id: str
    steps: Optional[List[Dict[str, Any]]]  # JSON stored in DB
    document_id: str
    generation_prompt: Optional[str]
    generation_context: Optional[str]
    status: str
    manual_review: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TestCase(TestCaseInDB):
    """Schema for test case responses."""
    pass


class TestCaseList(BaseModel):
    """Schema for test case list responses."""
    test_cases: List[TestCase]
    total: int
    page: int
    per_page: int


class TestCaseGeneration(BaseModel):
    """Schema for test case generation requests."""
    document_ids: List[str] = Field(..., description="Source document IDs")
    requirements: Optional[str] = Field(None, description="Specific requirements to focus on")
    test_type: Optional[str] = Field("functional", description="Type of tests to generate")
    priority: Optional[str] = Field("medium", description="Default priority for generated tests")
    count: Optional[int] = Field(10, description="Number of test cases to generate")


class TestCaseGenerationResponse(BaseModel):
    """Schema for test case generation responses."""
    task_id: str
    status: str
    message: str