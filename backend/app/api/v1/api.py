"""
API router for v1 endpoints.
"""
from fastapi import APIRouter

from app.api.v1.endpoints import documents, test_cases, mind_maps

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(
    documents.router,
    prefix="/documents",
    tags=["documents"]
)

api_router.include_router(
    test_cases.router,
    prefix="/testcases",
    tags=["test-cases"]
)

api_router.include_router(
    mind_maps.router,
    prefix="/mindmaps",
    tags=["mind-maps"]
)