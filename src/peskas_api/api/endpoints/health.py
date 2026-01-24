"""Health check endpoint (no auth required)."""

import logging

from fastapi import APIRouter

from peskas_api.api.deps import get_gcs_service
from peskas_api.core.config import get_settings
from peskas_api.models.responses import HealthResponse

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Health check endpoint with GCS connectivity test.

    Returns service status, version, and GCS bucket accessibility.
    No authentication required.
    
    Returns:
        - status: "healthy" if all systems operational, "degraded" if GCS unavailable
        - version: API version
        - gcs_accessible: Boolean indicating if GCS bucket is accessible
    """
    settings = get_settings()
    
    # Test GCS connectivity
    gcs_accessible = True
    try:
        gcs = get_gcs_service()
        # Quick check - just verify bucket exists
        gcs.bucket.exists()
    except Exception as e:
        logger.warning(f"Health check: GCS connection test failed - {e}")
        gcs_accessible = False
    
    status = "healthy" if gcs_accessible else "degraded"
    
    return HealthResponse(
        status=status,
        version=settings.api_version,
        gcs_accessible=gcs_accessible,
    )
