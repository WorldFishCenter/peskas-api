"""
Shared API dependencies.

FastAPI dependencies for authentication, services, etc.
"""

import logging
from typing import Annotated

from fastapi import Depends, HTTPException, Request

from peskas_api.core.auth import verify_api_key
from peskas_api.models.params import DatasetQueryParams
from peskas_api.models.permissions import APIKeyConfig
from peskas_api.services.audit import get_audit_service
from peskas_api.services.gcs import GCSService, get_gcs_service
from peskas_api.services.permissions import PermissionValidator
from peskas_api.services.query import QueryService, get_query_service

logger = logging.getLogger(__name__)

# Type aliases for cleaner endpoint signatures
AuthenticatedUser = Annotated[APIKeyConfig, Depends(verify_api_key)]
GCS = Annotated[GCSService, Depends(get_gcs_service)]
Query = Annotated[QueryService, Depends(get_query_service)]


async def validate_permissions(
    auth: AuthenticatedUser,
    params: DatasetQueryParams = Depends(),
    request: Request = None,
    audit_service = Depends(get_audit_service),
) -> DatasetQueryParams:
    """
    Dependency that validates query parameters against API key permissions.

    This should be used in endpoints that need permission checking.

    Args:
        auth: Authenticated API key configuration
        params: Query parameters to validate
        request: FastAPI request object (for endpoint path and client IP)

    Returns:
        Validated query parameters (same as input)

    Raises:
        HTTPException: 403 if permission validation fails
    """
    # Get endpoint path and client IP for logging
    endpoint_path = request.url.path if request else None
    client_ip = request.client.host if request and request.client else "unknown"

    # Create permission validator
    validator = PermissionValidator(auth.permissions)

    # Convert params to dict for audit logging
    query_params_dict = {
        "country": params.country,
        "status": params.status.value,
        "date_from": params.date_from.isoformat() if params.date_from else None,
        "date_to": params.date_to.isoformat() if params.date_to else None,
        "gaul_1": params.gaul_1,
        "gaul_2": params.gaul_2,
        "catch_taxon": params.catch_taxon,
        "survey_id": params.survey_id,
        "scope": params.scope,
        "limit": params.limit,
        "format": params.format.value,
    }

    try:
        # Validate parameters against permissions
        validator.validate_query_params(params, endpoint_path)

        # Log successful permission check
        api_key_id = "N/A"  # Will be set properly when we have the actual key
        await audit_service.log_permission_check(
            api_key_name=auth.name,
            api_key_id=api_key_id,
            endpoint=endpoint_path or "",
            client_ip=client_ip,
            query_params=query_params_dict,
            allowed=True,
            error_message=None,
        )

        logger.info(f"Permission check passed for {auth.name}: {endpoint_path}")

    except HTTPException as e:
        # Log permission denial
        await audit_service.log_permission_check(
            api_key_name=auth.name,
            api_key_id="N/A",
            endpoint=endpoint_path or "",
            client_ip=client_ip,
            query_params=query_params_dict,
            allowed=False,
            error_message=e.detail,
        )

        logger.warning(f"Permission denied for {auth.name}: {e.detail}")
        raise

    return params


# Type alias for validated parameters with permissions
ValidatedParams = Annotated[DatasetQueryParams, Depends(validate_permissions)]
