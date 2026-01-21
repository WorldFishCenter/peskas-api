"""
Authentication via shared secret header.

Simple but effective for internal/trusted clients.
"""

from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN

from peskas_api.core.config import get_settings

settings = get_settings()

api_key_header = APIKeyHeader(
    name=settings.api_key_header_name,
    auto_error=False,
)


async def verify_api_key(
    api_key: str | None = Security(api_key_header),
) -> str:
    """
    Dependency that validates the API key from request headers.

    Raises:
        HTTPException: 401 if header missing, 403 if key invalid

    Returns:
        The validated API key (for logging/audit purposes)
    """
    if api_key is None:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Missing API key. Include X-API-Key header.",
        )

    if api_key != settings.api_secret_key:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Invalid API key.",
        )

    return api_key
