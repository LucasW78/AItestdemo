"""
Mind map service for handling mind map operations.
"""
import uuid
import logging
from typing import List, Tuple, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.schemas.mind_map import MindMapCreate, MindMapUpdate, MindMapGeneration
from app.models.mind_map import MindMap as MindMapModel
from app.models.test_case import TestCase as TestCaseModel

logger = logging.getLogger(__name__)


class MindMapService:
    """
    Service for mind map management operations.
    """

    def __init__(self, db: Session):
        self.db = db

    async def create_mind_map(self, mind_map_create: MindMapCreate) -> MindMapModel:
        """
        Create a new mind map.
        """
        try:
            # Generate unique ID
            mind_map_id = str(uuid.uuid4())

            # Convert nodes and edges to dict
            nodes_data = [node.dict() for node in mind_map_create.nodes]
            edges_data = [edge.dict() for edge in mind_map_create.edges]

            # Create mind map record
            db_mind_map = MindMapModel(
                id=mind_map_id,
                title=mind_map_create.title,
                description=mind_map_create.description,
                nodes=nodes_data,
                edges=edges_data,
                test_case_ids=mind_map_create.test_case_ids,
                layout=mind_map_create.layout.dict() if mind_map_create.layout else None,
                generation_config=mind_map_create.generation_config
            )

            self.db.add(db_mind_map)
            self.db.commit()
            self.db.refresh(db_mind_map)

            logger.info(f"Mind map created: {mind_map_id}")
            return db_mind_map

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating mind map: {e}")
            raise

    async def get_mind_map(self, mind_map_id: str) -> Optional[MindMapModel]:
        """
        Get a mind map by ID.
        """
        try:
            mind_map = self.db.query(MindMapModel).filter(
                MindMapModel.id == mind_map_id
            ).first()
            return mind_map

        except Exception as e:
            logger.error(f"Error retrieving mind map {mind_map_id}: {e}")
            raise

    async def list_mind_maps(
        self,
        page: int = 1,
        per_page: int = 20,
        status: Optional[str] = None
    ) -> Tuple[List[MindMapModel], int]:
        """
        List mind maps with pagination and filtering.
        """
        try:
            query = self.db.query(MindMapModel)

            # Apply filters
            if status:
                query = query.filter(MindMapModel.status == status)

            # Count total records
            total = query.count()

            # Apply pagination
            offset = (page - 1) * per_page
            mind_maps = query.order_by(desc(MindMapModel.created_at)).offset(
                offset
            ).limit(per_page).all()

            return mind_maps, total

        except Exception as e:
            logger.error(f"Error listing mind maps: {e}")
            raise

    async def update_mind_map(
        self,
        mind_map_id: str,
        mind_map_update: MindMapUpdate
    ) -> Optional[MindMapModel]:
        """
        Update a mind map.
        """
        try:
            mind_map = self.db.query(MindMapModel).filter(
                MindMapModel.id == mind_map_id
            ).first()

            if not mind_map:
                return None

            # Update fields
            update_data = mind_map_update.dict(exclude_unset=True)

            # Handle nodes, edges, and layout conversion
            if 'nodes' in update_data and update_data['nodes']:
                update_data['nodes'] = [node.dict() for node in update_data['nodes']]

            if 'edges' in update_data and update_data['edges']:
                update_data['edges'] = [edge.dict() for edge in update_data['edges']]

            if 'layout' in update_data and update_data['layout']:
                update_data['layout'] = update_data['layout'].dict()

            for field, value in update_data.items():
                setattr(mind_map, field, value)

            # Increment version
            mind_map.version += 1

            self.db.commit()
            self.db.refresh(mind_map)

            logger.info(f"Mind map updated: {mind_map_id}")
            return mind_map

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating mind map {mind_map_id}: {e}")
            raise

    async def delete_mind_map(self, mind_map_id: str) -> bool:
        """
        Delete a mind map.
        """
        try:
            mind_map = self.db.query(MindMapModel).filter(
                MindMapModel.id == mind_map_id
            ).first()

            if not mind_map:
                return False

            self.db.delete(mind_map)
            self.db.commit()

            logger.info(f"Mind map deleted: {mind_map_id}")
            return True

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting mind map {mind_map_id}: {e}")
            raise

    async def generate_mind_map(self, generation_request: MindMapGeneration) -> str:
        """
        Generate a mind map from test cases.
        """
        try:
            # Generate task ID
            task_id = str(uuid.uuid4())

            # TODO: Implement actual AI mind map generation
            # This will include:
            # 1. Retrieve test cases from database
            # 2. Analyze test case structure and relationships
            # 3. Generate mind map nodes and edges
            # 4. Apply layout algorithm
            # 5. Store mind map in database

            # For now, create a sample mind map
            from app.schemas.mind_map import MindMapNode, MindMapEdge, MindMapLayout

            # Create sample nodes
            root_node = MindMapNode(
                id="root",
                label=generation_request.title or "Test Cases",
                type="root",
                x=0,
                y=0,
                color="#FF6B6B",
                size=20
            )

            # Create sample mind map
            sample_mind_map = MindMapCreate(
                title=generation_request.title or "Generated Mind Map",
                description="Mind map generated from test cases",
                nodes=[root_node],
                edges=[],
                test_case_ids=generation_request.test_case_ids,
                layout=MindMapLayout(
                    algorithm="hierarchical",
                    direction="TB",
                    node_spacing=100,
                    level_spacing=150
                ),
                generation_config=generation_request.dict()
            )

            await self.create_mind_map(sample_mind_map)

            logger.info(f"Mind map generation task started: {task_id}")
            return task_id

        except Exception as e:
            logger.error(f"Error generating mind map: {e}")
            raise

    async def get_generation_status(self, task_id: str) -> Dict[str, Any]:
        """
        Get mind map generation task status.
        """
        try:
            # TODO: Implement actual task status tracking
            # For now, return completed status
            return {
                "task_id": task_id,
                "status": "completed",
                "progress": 100,
                "message": "Mind map generation completed",
                "results": {
                    "mind_map_id": "sample_mind_map_id",
                    "node_count": 1,
                    "edge_count": 0
                }
            }

        except Exception as e:
            logger.error(f"Error getting generation status {task_id}: {e}")
            raise