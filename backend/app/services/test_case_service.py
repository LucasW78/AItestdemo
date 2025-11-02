"""
Test case service for handling test case operations.
"""
import uuid
import logging
from typing import List, Tuple, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.schemas.test_case import TestCaseCreate, TestCaseUpdate, TestCaseGeneration
from app.models.test_case import TestCase as TestCaseModel
from app.models.document import Document as DocumentModel

logger = logging.getLogger(__name__)


class TestCaseService:
    """
    Service for test case management operations.
    """

    def __init__(self, db: Session):
        self.db = db

    async def create_test_case(self, test_case_create: TestCaseCreate) -> TestCaseModel:
        """
        Create a new test case.
        """
        try:
            # Generate unique ID
            test_case_id = str(uuid.uuid4())

            # Convert steps to dict if provided
            steps_data = None
            if test_case_create.steps:
                steps_data = [step.dict() for step in test_case_create.steps]

            # Create test case record
            db_test_case = TestCaseModel(
                id=test_case_id,
                title=test_case_create.title,
                description=test_case_create.description,
                preconditions=test_case_create.preconditions,
                steps=steps_data,
                expected_result=test_case_create.expected_result,
                priority=test_case_create.priority,
                category=test_case_create.category,
                tags=test_case_create.tags,
                document_id=test_case_create.document_id,
                generation_prompt=test_case_create.generation_prompt,
                generation_context=test_case_create.generation_context
            )

            self.db.add(db_test_case)
            self.db.commit()
            self.db.refresh(db_test_case)

            logger.info(f"Test case created: {test_case_id}")
            return db_test_case

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating test case: {e}")
            raise

    async def get_test_case(self, test_case_id: str) -> Optional[TestCaseModel]:
        """
        Get a test case by ID.
        """
        try:
            test_case = self.db.query(TestCaseModel).filter(
                TestCaseModel.id == test_case_id
            ).first()
            return test_case

        except Exception as e:
            logger.error(f"Error retrieving test case {test_case_id}: {e}")
            raise

    async def list_test_cases(
        self,
        page: int = 1,
        per_page: int = 20,
        document_id: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None
    ) -> Tuple[List[TestCaseModel], int]:
        """
        List test cases with pagination and filtering.
        """
        try:
            query = self.db.query(TestCaseModel)

            # Apply filters
            if document_id:
                query = query.filter(TestCaseModel.document_id == document_id)
            if status:
                query = query.filter(TestCaseModel.status == status)
            if priority:
                query = query.filter(TestCaseModel.priority == priority)

            # Count total records
            total = query.count()

            # Apply pagination
            offset = (page - 1) * per_page
            test_cases = query.order_by(desc(TestCaseModel.created_at)).offset(
                offset
            ).limit(per_page).all()

            return test_cases, total

        except Exception as e:
            logger.error(f"Error listing test cases: {e}")
            raise

    async def update_test_case(
        self,
        test_case_id: str,
        test_case_update: TestCaseUpdate
    ) -> Optional[TestCaseModel]:
        """
        Update a test case.
        """
        try:
            test_case = self.db.query(TestCaseModel).filter(
                TestCaseModel.id == test_case_id
            ).first()

            if not test_case:
                return None

            # Update fields
            update_data = test_case_update.dict(exclude_unset=True)

            # Handle steps conversion
            if 'steps' in update_data and update_data['steps']:
                update_data['steps'] = [step.dict() for step in update_data['steps']]

            for field, value in update_data.items():
                setattr(test_case, field, value)

            self.db.commit()
            self.db.refresh(test_case)

            logger.info(f"Test case updated: {test_case_id}")
            return test_case

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating test case {test_case_id}: {e}")
            raise

    async def delete_test_case(self, test_case_id: str) -> bool:
        """
        Delete a test case.
        """
        try:
            test_case = self.db.query(TestCaseModel).filter(
                TestCaseModel.id == test_case_id
            ).first()

            if not test_case:
                return False

            self.db.delete(test_case)
            self.db.commit()

            logger.info(f"Test case deleted: {test_case_id}")
            return True

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting test case {test_case_id}: {e}")
            raise

    async def generate_test_cases(self, generation_request: TestCaseGeneration) -> str:
        """
        Generate test cases using AI from documents.
        """
        try:
            # Generate task ID
            task_id = str(uuid.uuid4())

            # TODO: Implement actual AI test case generation
            # This will include:
            # 1. Retrieve documents from RAG system
            # 2. Generate context using retrieved documents
            # 3. Call Gemini API to generate test cases
            # 4. Parse and validate generated test cases
            # 5. Store test cases in database

            # For now, create a sample test case
            sample_test_case = TestCaseCreate(
                title="Sample Generated Test Case",
                description="This is a sample test case generated by AI",
                preconditions="System is running and accessible",
                steps=[
                    {
                        "step_number": 1,
                        "action": "Navigate to application",
                        "expected_result": "Application loads successfully"
                    },
                    {
                        "step_number": 2,
                        "action": "Perform test action",
                        "expected_result": "Action completes as expected"
                    }
                ],
                expected_result="Test passes successfully",
                priority=generation_request.priority or "medium",
                document_id=generation_request.document_ids[0] if generation_request.document_ids else "sample",
                generation_prompt=generation_request.requirements or "Generate test cases",
                generation_context="Sample context for test case generation"
            )

            await self.create_test_case(sample_test_case)

            logger.info(f"Test case generation task started: {task_id}")
            return task_id

        except Exception as e:
            logger.error(f"Error generating test cases: {e}")
            raise

    async def get_generation_status(self, task_id: str) -> Dict[str, Any]:
        """
        Get test case generation task status.
        """
        try:
            # TODO: Implement actual task status tracking
            # For now, return completed status
            return {
                "task_id": task_id,
                "status": "completed",
                "progress": 100,
                "message": "Test case generation completed",
                "results": {
                    "generated_count": 1,
                    "test_case_ids": ["sample_test_case_id"]
                }
            }

        except Exception as e:
            logger.error(f"Error getting generation status {task_id}: {e}")
            raise