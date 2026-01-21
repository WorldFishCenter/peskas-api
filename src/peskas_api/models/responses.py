"""Response schemas."""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = "healthy"
    version: str


class ErrorResponse(BaseModel):
    """Standard error response."""

    detail: str
