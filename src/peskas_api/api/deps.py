"""
Shared API dependencies.

FastAPI dependencies for authentication, services, etc.
"""

from typing import Annotated

from fastapi import Depends

from peskas_api.core.auth import verify_api_key
from peskas_api.services.gcs import GCSService, get_gcs_service
from peskas_api.services.query import QueryService, get_query_service

# Type aliases for cleaner endpoint signatures
AuthenticatedUser = Annotated[str, Depends(verify_api_key)]
GCS = Annotated[GCSService, Depends(get_gcs_service)]
Query = Annotated[QueryService, Depends(get_query_service)]
