"""Health check endpoint (no auth required)."""

from fastapi import APIRouter

from peskas_api.core.config import get_settings
from peskas_api.models.responses import HealthResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Health check endpoint.

    Returns service status and version. No authentication required.
    """
    settings = get_settings()
    return HealthResponse(
        status="healthy",
        version=settings.api_version,
    )
