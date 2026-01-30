"""
Authentication via API key with granular permissions.

Supports multiple API keys with different permission levels.
"""

import logging

from fastapi import Depends, HTTPException, Request, Security
from fastapi.security import APIKeyHeader
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN

from peskas_api.core.config import get_settings
from peskas_api.models.permissions import APIKeyConfig
from peskas_api.services.api_keys import get_api_key_service
from peskas_api.services.audit import get_audit_service

logger = logging.getLogger(__name__)
settings = get_settings()

api_key_header = APIKeyHeader(
    name=settings.api_key_header_name,
    auto_error=False,
)


async def verify_api_key(
    request: Request,
    api_key: str | None = Security(api_key_header),
    audit_service = Depends(get_audit_service),
) -> APIKeyConfig:
    """
    Dependency that validates the API key from request headers.

    Returns the full API key configuration including permissions,
    which can be used by downstream dependencies for authorization.

    Raises:
        HTTPException: 401 if header missing, 403 if key invalid

    Returns:
        APIKeyConfig with permissions and metadata
    """
    # Get client IP for audit logging
    client_ip = request.client.host if request.client else "unknown"
    endpoint = request.url.path

    if api_key is None:
        # Log failed auth attempt
        await audit_service.log_auth_failure(
            client_ip=client_ip,
            endpoint=endpoint,
            error_message="Missing API key header"
        )
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Missing API key. Include X-API-Key header.",
        )

    # Look up key in registry
    api_key_service = get_api_key_service()
    key_config = api_key_service.get_key_config(api_key)

    if key_config is None:
        # Log failed auth attempt
        await audit_service.log_auth_failure(
            client_ip=client_ip,
            endpoint=endpoint,
            error_message="Invalid API key"
        )
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Invalid API key.",
        )

    if not key_config.enabled:
        # Log failed auth attempt
        await audit_service.log_auth_failure(
            client_ip=client_ip,
            endpoint=endpoint,
            error_message=f"Disabled API key: {key_config.name}"
        )
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="API key is disabled.",
        )

    # Log successful authentication
    api_key_id = api_key[:8] + "..." if len(api_key) > 8 else api_key
    await audit_service.log_auth_success(
        api_key_name=key_config.name,
        api_key_id=api_key_id,
        endpoint=endpoint,
        client_ip=client_ip,
    )

    logger.info(f"API key authenticated: {key_config.name} (key_id: {api_key_id})")

    return key_config
