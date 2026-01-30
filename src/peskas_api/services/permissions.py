"""
Permission validation service.

Validates query parameters against API key permissions.
"""

import logging
from datetime import date

from fastapi import HTTPException
from starlette.status import HTTP_403_FORBIDDEN

from peskas_api.models.params import DatasetQueryParams
from peskas_api.models.permissions import APIKeyPermissions

logger = logging.getLogger(__name__)


class PermissionValidator:
    """Validates query parameters against API key permissions."""

    def __init__(self, permissions: APIKeyPermissions):
        """
        Initialize validator with permissions.

        Args:
            permissions: The permissions to validate against
        """
        self.permissions = permissions

    def validate_query_params(
        self,
        params: DatasetQueryParams,
        endpoint_path: str | None = None,
    ) -> None:
        """
        Validate query parameters against permissions.

        Args:
            params: Query parameters to validate
            endpoint_path: Optional endpoint path for endpoint-level permissions

        Raises:
            HTTPException: 403 if validation fails
        """
        # If allow_all, skip all checks
        if self.permissions.allow_all:
            return

        # Validate endpoint access (if endpoint restrictions exist)
        if endpoint_path and self.permissions.endpoints is not None:
            if not self._is_endpoint_allowed(endpoint_path):
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN,
                    detail="Access denied: Your API key does not have access to this endpoint"
                )

        # Validate country
        if self.permissions.countries is not None:
            if params.country.lower() not in self.permissions.countries:
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN,
                    detail=f"Access denied: Your API key cannot access country '{params.country}'. "
                           f"Allowed countries: {', '.join(self.permissions.countries)}"
                )

        # Validate status
        if self.permissions.statuses is not None:
            if params.status.value.lower() not in self.permissions.statuses:
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN,
                    detail=f"Access denied: Your API key cannot access '{params.status.value}' data. "
                           f"Allowed statuses: {', '.join(self.permissions.statuses)}"
                )

        # Validate date range
        if params.date_from is not None or params.date_to is not None:
            self._validate_date_range(params.date_from, params.date_to)

        # Validate GAUL codes
        if params.gaul_1 is not None:
            self._validate_filter_value(
                "gaul_1",
                params.gaul_1,
                self.permissions.gaul_1,
                "GAUL level 1 code"
            )

        if params.gaul_2 is not None:
            self._validate_filter_value(
                "gaul_2",
                params.gaul_2,
                self.permissions.gaul_2,
                "GAUL level 2 code"
            )

        # Validate catch taxon
        if params.catch_taxon is not None:
            self._validate_filter_value(
                "catch_taxon",
                params.catch_taxon,
                self.permissions.catch_taxon,
                "species code"
            )

        # Validate survey_id
        if params.survey_id is not None:
            self._validate_filter_value(
                "survey_id",
                params.survey_id,
                self.permissions.survey_id,
                "survey ID"
            )

        # Validate limit
        if params.limit is not None and self.permissions.max_limit is not None:
            if params.limit > self.permissions.max_limit:
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN,
                    detail=f"Access denied: Your API key's maximum limit is {self.permissions.max_limit}. "
                           f"Requested: {params.limit}"
                )

    def _is_endpoint_allowed(self, endpoint_path: str) -> bool:
        """Check if endpoint is in allowed list (with wildcard support)."""
        if self.permissions.endpoints is None:
            return True

        for pattern in self.permissions.endpoints:
            # Simple wildcard matching: /api/v1/metadata/* matches /api/v1/metadata/anything
            if pattern.endswith("*"):
                prefix = pattern[:-1]  # Remove *
                if endpoint_path.startswith(prefix):
                    return True
            elif pattern == endpoint_path:
                return True

        return False

    def _validate_date_range(
        self,
        requested_from: date | None,
        requested_to: date | None,
    ) -> None:
        """Validate date range against permissions."""
        # Check if requested date_from is before allowed date_from
        if self.permissions.date_from is not None:
            if requested_from is None:
                # User didn't specify date_from, but permission requires minimum date
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN,
                    detail=f"Access denied: Your API key requires date_from >= {self.permissions.date_from.isoformat()}"
                )
            if requested_from < self.permissions.date_from:
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN,
                    detail=f"Access denied: Your API key cannot query data before {self.permissions.date_from.isoformat()}. "
                           f"Requested: {requested_from.isoformat()}"
                )

        # Check if requested date_to is after allowed date_to
        if self.permissions.date_to is not None:
            if requested_to is not None and requested_to > self.permissions.date_to:
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN,
                    detail=f"Access denied: Your API key cannot query data after {self.permissions.date_to.isoformat()}. "
                           f"Requested: {requested_to.isoformat()}"
                )

    def _validate_filter_value(
        self,
        param_name: str,
        requested_value: str,
        allowed_values: list[str] | None,
        human_name: str,
    ) -> None:
        """Validate a single filter value against allowed values."""
        if allowed_values is not None:
            if requested_value.lower() not in allowed_values:
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN,
                    detail=f"Access denied: Your API key cannot filter by {human_name} '{requested_value}'. "
                           f"Allowed values: {', '.join(allowed_values)}"
                )
