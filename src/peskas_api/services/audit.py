"""
Audit logging service for MongoDB.

Tracks API key usage, authentication events, and permission checks.
"""

import logging
from datetime import datetime
from functools import lru_cache
from typing import Any

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection

from peskas_api.core.config import get_settings
from peskas_api.models.audit import AuditLog

logger = logging.getLogger(__name__)


class AuditService:
    """Service for logging API key usage to MongoDB."""

    def __init__(self):
        """Initialize audit service with MongoDB connection."""
        settings = get_settings()
        self.client: AsyncIOMotorClient | None = None
        self.collection: AsyncIOMotorCollection | None = None
        self.mongodb_uri = settings.mongodb_uri
        self.database_name = settings.mongodb_database
        self.collection_name = settings.mongodb_audit_collection
        self._initialized = False

    async def _ensure_initialized(self) -> None:
        """Ensure MongoDB connection is initialized."""
        if self._initialized:
            return

        try:
            self.client = AsyncIOMotorClient(self.mongodb_uri)
            db = self.client[self.database_name]
            self.collection = db[self.collection_name]

            # Create indexes for common queries
            await self.collection.create_index("timestamp")
            await self.collection.create_index("api_key_name")
            await self.collection.create_index("event_type")
            await self.collection.create_index([("timestamp", -1)])  # Descending for recent-first queries

            self._initialized = True
            logger.info(f"MongoDB audit logging initialized: {self.database_name}.{self.collection_name}")

        except Exception as e:
            logger.error(f"Failed to initialize MongoDB audit logging: {e}", exc_info=True)
            # Don't raise - allow app to continue even if audit logging fails
            # We'll log errors but won't block the API

    async def _log_event(self, audit_log: AuditLog) -> None:
        """
        Log an audit event to MongoDB.

        Args:
            audit_log: The audit log entry to save
        """
        try:
            await self._ensure_initialized()

            if self.collection is None:
                logger.warning("MongoDB collection not initialized, skipping audit log")
                return

            document = audit_log.to_mongo_dict()
            await self.collection.insert_one(document)

        except Exception as e:
            # Log error but don't raise - audit logging should not break the API
            logger.error(f"Failed to write audit log: {e}", exc_info=True)

    async def log_auth_success(
        self,
        api_key_name: str,
        api_key_id: str,
        endpoint: str,
        client_ip: str,
    ) -> None:
        """
        Log successful authentication.

        Args:
            api_key_name: Human-readable name of the API key
            api_key_id: Truncated API key (first 8 chars)
            endpoint: API endpoint path
            client_ip: Client IP address
        """
        audit_log = AuditLog(
            timestamp=datetime.utcnow(),
            api_key_name=api_key_name,
            api_key_id=api_key_id,
            event_type="auth_success",
            endpoint=endpoint,
            method="GET",
            client_ip=client_ip,
            query_params={},
            status_code=None,
            error_message=None,
            duration_ms=None,
        )
        await self._log_event(audit_log)

    async def log_auth_failure(
        self,
        client_ip: str,
        endpoint: str,
        error_message: str,
    ) -> None:
        """
        Log failed authentication attempt.

        Args:
            client_ip: Client IP address
            endpoint: API endpoint path
            error_message: Error message describing the failure
        """
        audit_log = AuditLog(
            timestamp=datetime.utcnow(),
            api_key_name="Unknown",
            api_key_id="N/A",
            event_type="auth_failure",
            endpoint=endpoint,
            method="GET",
            client_ip=client_ip,
            query_params={},
            status_code=None,
            error_message=error_message,
            duration_ms=None,
        )
        await self._log_event(audit_log)

    async def log_permission_check(
        self,
        api_key_name: str,
        api_key_id: str,
        endpoint: str,
        client_ip: str,
        query_params: dict[str, Any],
        allowed: bool,
        error_message: str | None = None,
    ) -> None:
        """
        Log permission validation result.

        Args:
            api_key_name: Human-readable name of the API key
            api_key_id: Truncated API key (first 8 chars)
            endpoint: API endpoint path
            client_ip: Client IP address
            query_params: Query parameters being validated
            allowed: Whether permission was granted
            error_message: Error message if permission denied
        """
        event_type = "permission_check" if allowed else "permission_denied"

        audit_log = AuditLog(
            timestamp=datetime.utcnow(),
            api_key_name=api_key_name,
            api_key_id=api_key_id,
            event_type=event_type,
            endpoint=endpoint,
            method="GET",
            client_ip=client_ip,
            country=query_params.get("country"),
            query_params=query_params,
            status_code=None,
            error_message=error_message,
            duration_ms=None,
        )
        await self._log_event(audit_log)

    async def log_data_access(
        self,
        api_key_name: str,
        api_key_id: str,
        endpoint: str,
        method: str,
        client_ip: str,
        query_params: dict[str, Any],
        status_code: int,
        duration_ms: float,
    ) -> None:
        """
        Log data access event with timing information.

        Args:
            api_key_name: Human-readable name of the API key
            api_key_id: Truncated API key (first 8 chars)
            endpoint: API endpoint path
            method: HTTP method
            client_ip: Client IP address
            query_params: Query parameters used
            status_code: HTTP response status code
            duration_ms: Request duration in milliseconds
        """
        audit_log = AuditLog(
            timestamp=datetime.utcnow(),
            api_key_name=api_key_name,
            api_key_id=api_key_id,
            event_type="data_access",
            endpoint=endpoint,
            method=method,
            client_ip=client_ip,
            country=query_params.get("country"),
            query_params=query_params,
            status_code=status_code,
            error_message=None,
            duration_ms=duration_ms,
        )
        await self._log_event(audit_log)

    async def close(self) -> None:
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            logger.info("MongoDB audit logging connection closed")


@lru_cache
def get_audit_service() -> AuditService:
    """
    Get cached audit service instance.

    Returns:
        Singleton AuditService instance
    """
    return AuditService()
