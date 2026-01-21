"""
Main API router.

Aggregates all endpoint routers.
"""

from fastapi import APIRouter

from peskas_api.api.endpoints import health, datasets

api_router = APIRouter()

# Health check (no prefix, no auth)
api_router.include_router(health.router)

# Dataset endpoints
api_router.include_router(datasets.router, prefix="/data")
