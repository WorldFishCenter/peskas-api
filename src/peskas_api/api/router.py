"""
Main API router.

Aggregates all endpoint routers.
"""

import logging

from fastapi import APIRouter

from peskas_api.api.endpoints import health, datasets

logger = logging.getLogger(__name__)

api_router = APIRouter()

# Health check (no prefix, no auth)
api_router.include_router(health.router)

# Dataset endpoints
api_router.include_router(datasets.router, prefix="/data")

# Metadata endpoints - import with error handling
try:
    from peskas_api.api.endpoints import metadata
    api_router.include_router(metadata.router)
    logger.info("Metadata endpoints registered successfully")
except Exception as e:
    logger.error(f"Failed to register metadata endpoints: {e}", exc_info=True)
    # Don't raise - allow app to start without metadata endpoints for debugging
    # In production, you may want to raise here
    raise
