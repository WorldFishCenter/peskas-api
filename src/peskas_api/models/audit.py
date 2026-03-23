"""
Audit log models for API key usage tracking.

Defines the structure of audit log entries stored in MongoDB.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class AuditLog(BaseModel):
    """
    Audit log entry for API key usage.

    Tracks authentication events, permission checks, and data access
    for security monitoring and usage analysis.
    """

    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the event occurred (UTC)"
    )

    api_key_name: str = Field(
        description="Human-readable name of the API key"
    )

    api_key_id: str = Field(
        description="Truncated API key for identification (first 8 chars)"
    )

    event_type: str = Field(
        description="Type of event: auth_success, auth_failure, permission_check, permission_denied, data_access"
    )

    endpoint: str = Field(
        description="API endpoint path"
    )

    method: str = Field(
        default="GET",
        description="HTTP method (GET, POST, etc.)"
    )

    client_ip: str = Field(
        description="IP address of the client making the request"
    )

    country: str | None = Field(
        default=None,
        description="Country parameter from query (if applicable)"
    )

    query_params: dict[str, Any] = Field(
        default_factory=dict,
        description="All query parameters from the request"
    )

    status_code: int | None = Field(
        default=None,
        description="HTTP response status code"
    )

    error_message: str | None = Field(
        default=None,
        description="Error message if the request failed"
    )

    duration_ms: float | None = Field(
        default=None,
        description="Request duration in milliseconds"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "timestamp": "2024-01-15T10:30:00Z",
                    "api_key_name": "Timor-Leste Research",
                    "api_key_id": "tls-rese",
                    "event_type": "data_access",
                    "endpoint": "/api/v1/data/landings",
                    "method": "GET",
                    "client_ip": "203.0.113.42",
                    "country": "tls",
                    "query_params": {
                        "country": "tls",
                        "status": "validated",
                        "date_from": "2024-01-01"
                    },
                    "status_code": 200,
                    "error_message": None,
                    "duration_ms": 1250.5
                }
            ]
        }
    }

    def to_mongo_dict(self) -> dict[str, Any]:
        """
        Convert to dictionary suitable for MongoDB insertion.

        Returns:
            Dictionary representation with proper field names
        """
        return self.model_dump(mode="json")
