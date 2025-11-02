"""
Mind map management API endpoints.
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_database
from app.schemas.mind_map import (
    MindMap, MindMapList, MindMapCreate, MindMapUpdate,
    MindMapGeneration, MindMapGenerationResponse
)
from app.models.mind_map import MindMap as MindMapModel
from app.services.mind_map_service import MindMapService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/generate", response_model=MindMapGenerationResponse, status_code=status.HTTP_202_ACCEPTED)
async def generate_mind_map(
    generation_request: MindMapGeneration,
    db: Session = Depends(get_database)
):
    """
    Generate a mind map from test cases.
    """
    mind_map_service = MindMapService(db)

    try:
        # Start mind map generation (async)
        task_id = await mind_map_service.generate_mind_map(generation_request)

        return MindMapGenerationResponse(
            task_id=task_id,
            status="processing",
            message="Mind map generation started successfully"
        )

    except Exception as e:
        logger.error(f"Error generating mind map: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating mind map: {str(e)}"
        )


@router.get("/", response_model=MindMapList)
async def list_mind_maps(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_database)
):
    """
    List mind maps with pagination and filtering.
    """
    mind_map_service = MindMapService(db)

    try:
        mind_maps, total = await mind_map_service.list_mind_maps(
            page=page,
            per_page=per_page,
            status=status
        )

        return MindMapList(
            mind_maps=mind_maps,
            total=total,
            page=page,
            per_page=per_page
        )

    except Exception as e:
        logger.error(f"Error listing mind maps: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving mind maps"
        )


@router.get("/{mind_map_id}", response_model=MindMap)
async def get_mind_map(
    mind_map_id: str,
    db: Session = Depends(get_database)
):
    """
    Get a specific mind map by ID.
    """
    mind_map_service = MindMapService(db)

    try:
        mind_map = await mind_map_service.get_mind_map(mind_map_id)
        if not mind_map:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mind map not found"
            )
        return mind_map

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving mind map {mind_map_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving mind map"
        )


@router.post("/", response_model=MindMap, status_code=status.HTTP_201_CREATED)
async def create_mind_map(
    mind_map_create: MindMapCreate,
    db: Session = Depends(get_database)
):
    """
    Create a new mind map.
    """
    mind_map_service = MindMapService(db)

    try:
        mind_map = await mind_map_service.create_mind_map(mind_map_create)
        logger.info(f"Mind map created successfully: {mind_map.id}")
        return mind_map

    except Exception as e:
        logger.error(f"Error creating mind map: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating mind map: {str(e)}"
        )


@router.put("/{mind_map_id}", response_model=MindMap)
async def update_mind_map(
    mind_map_id: str,
    mind_map_update: MindMapUpdate,
    db: Session = Depends(get_database)
):
    """
    Update a mind map.
    """
    mind_map_service = MindMapService(db)

    try:
        mind_map = await mind_map_service.update_mind_map(mind_map_id, mind_map_update)
        if not mind_map:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mind map not found"
            )
        return mind_map

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating mind map {mind_map_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating mind map"
        )


@router.delete("/{mind_map_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_mind_map(
    mind_map_id: str,
    db: Session = Depends(get_database)
):
    """
    Delete a mind map.
    """
    mind_map_service = MindMapService(db)

    try:
        success = await mind_map_service.delete_mind_map(mind_map_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mind map not found"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting mind map {mind_map_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting mind map"
        )


@router.get("/generation/{task_id}/status")
async def get_generation_status(
    task_id: str,
    db: Session = Depends(get_database)
):
    """
    Get mind map generation task status.
    """
    mind_map_service = MindMapService(db)

    try:
        status = await mind_map_service.get_generation_status(task_id)
        return status

    except Exception as e:
        logger.error(f"Error getting generation status {task_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving generation status"
        )