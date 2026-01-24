"""Response schemas."""

from typing import Literal

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Health check response."""

    status: Literal["healthy", "degraded"] = Field(
        default="healthy",
        description="Service health status"
    )
    version: str = Field(description="API version")
    gcs_accessible: bool = Field(
        default=True,
        description="Whether GCS bucket is accessible"
    )


class ErrorResponse(BaseModel):
    """Standard error response."""

    detail: str
