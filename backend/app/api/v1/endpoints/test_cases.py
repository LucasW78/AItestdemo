"""
Test case management API endpoints.
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_database
from app.schemas.test_case import (
    TestCase, TestCaseList, TestCaseCreate, TestCaseUpdate,
    TestCaseGeneration, TestCaseGenerationResponse
)
from app.models.test_case import TestCase as TestCaseModel
from app.services.test_case_service import TestCaseService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/generate", response_model=TestCaseGenerationResponse, status_code=status.HTTP_202_ACCEPTED)
async def generate_test_cases(
    generation_request: TestCaseGeneration,
    db: Session = Depends(get_database)
):
    """
    Generate test cases using AI from documents.
    """
    test_case_service = TestCaseService(db)

    try:
        # Start test case generation (async)
        task_id = await test_case_service.generate_test_cases(generation_request)

        return TestCaseGenerationResponse(
            task_id=task_id,
            status="processing",
            message="Test case generation started successfully"
        )

    except Exception as e:
        logger.error(f"Error generating test cases: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating test cases: {str(e)}"
        )


@router.get("/", response_model=TestCaseList)
async def list_test_cases(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    document_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    db: Session = Depends(get_database)
):
    """
    List test cases with pagination and filtering.
    """
    test_case_service = TestCaseService(db)

    try:
        test_cases, total = await test_case_service.list_test_cases(
            page=page,
            per_page=per_page,
            document_id=document_id,
            status=status,
            priority=priority
        )

        return TestCaseList(
            test_cases=test_cases,
            total=total,
            page=page,
            per_page=per_page
        )

    except Exception as e:
        logger.error(f"Error listing test cases: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving test cases"
        )


@router.get("/{test_case_id}", response_model=TestCase)
async def get_test_case(
    test_case_id: str,
    db: Session = Depends(get_database)
):
    """
    Get a specific test case by ID.
    """
    test_case_service = TestCaseService(db)

    try:
        test_case = await test_case_service.get_test_case(test_case_id)
        if not test_case:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test case not found"
            )
        return test_case

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving test case {test_case_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving test case"
        )


@router.post("/", response_model=TestCase, status_code=status.HTTP_201_CREATED)
async def create_test_case(
    test_case_create: TestCaseCreate,
    db: Session = Depends(get_database)
):
    """
    Create a new test case.
    """
    test_case_service = TestCaseService(db)

    try:
        test_case = await test_case_service.create_test_case(test_case_create)
        logger.info(f"Test case created successfully: {test_case.id}")
        return test_case

    except Exception as e:
        logger.error(f"Error creating test case: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating test case: {str(e)}"
        )


@router.put("/{test_case_id}", response_model=TestCase)
async def update_test_case(
    test_case_id: str,
    test_case_update: TestCaseUpdate,
    db: Session = Depends(get_database)
):
    """
    Update a test case.
    """
    test_case_service = TestCaseService(db)

    try:
        test_case = await test_case_service.update_test_case(test_case_id, test_case_update)
        if not test_case:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test case not found"
            )
        return test_case

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating test case {test_case_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating test case"
        )


@router.delete("/{test_case_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_test_case(
    test_case_id: str,
    db: Session = Depends(get_database)
):
    """
    Delete a test case.
    """
    test_case_service = TestCaseService(db)

    try:
        success = await test_case_service.delete_test_case(test_case_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test case not found"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting test case {test_case_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting test case"
        )


@router.get("/generation/{task_id}/status")
async def get_generation_status(
    task_id: str,
    db: Session = Depends(get_database)
):
    """
    Get test case generation task status.
    """
    test_case_service = TestCaseService(db)

    try:
        status = await test_case_service.get_generation_status(task_id)
        return status

    except Exception as e:
        logger.error(f"Error getting generation status {task_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving generation status"
        )