"""
Metadata endpoints.

Endpoints for retrieving field/column metadata for datasets.
This allows users to discover what fields are available, their types,
descriptions, units, and possible values.

These endpoints follow semantic web and FAIR data principles by providing
machine-readable field definitions with ontology URLs where available.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query

from peskas_api.api.deps import AuthenticatedUser
from peskas_api.models.responses import DatasetMetadataResponse, FieldMetadataResponse, MetadataListResponse
from peskas_api.schema.dataset_config import get_all_dataset_types, get_dataset_type
from peskas_api.schema.field_metadata import (
    get_all_fields_metadata,
    get_fields_metadata_by_scope,
    get_field_metadata,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Metadata"])


@router.get(
    "/metadata",
    response_model=MetadataListResponse,
    summary="List available dataset types",
    description="Get a list of all available dataset types that have metadata available.",
)
async def list_dataset_types(
    _auth: AuthenticatedUser,
):
    """
    List all available dataset types with metadata.

    Returns a list of dataset type names that can be used to query
    detailed field metadata.

    Returns:
        MetadataListResponse: List of available dataset type names

    Raises:
        401: If API key is missing or invalid
    """
    dataset_types = get_all_dataset_types()
    dataset_names = [ds_type.name for ds_type in dataset_types]
    logger.info(f"Listed {len(dataset_names)} dataset types: {', '.join(dataset_names)}")
    return MetadataListResponse(dataset_types=dataset_names)


@router.get(
    "/metadata/{dataset_type}",
    response_model=DatasetMetadataResponse,
    summary="Get dataset field metadata",
    description="Get detailed metadata for all fields in a dataset type, including descriptions, data types, units, and possible values.",
)
async def get_dataset_metadata(
    dataset_type: str,
    scope: str | None = Query(
        default=None,
        description="Optional scope name to filter fields (e.g., 'trip_info', 'catch_info'). If provided, only returns metadata for fields in that scope.",
    ),
    _auth: AuthenticatedUser = Depends(),
):
    """
    Get field metadata for a dataset type.

    Returns comprehensive metadata for each field including:
    - Description
    - Data type
    - Units (if applicable)
    - Possible values (for categorical fields)
    - Value ranges (for numeric fields)
    - Examples

    Args:
        dataset_type: Dataset type name (e.g., 'landings')
        scope: Optional scope name to filter fields

    Returns:
        DatasetMetadataResponse with field metadata

    Raises:
        401: If API key is missing or invalid
        404: If dataset type not found
        400: If scope is invalid
    """
    # Validate dataset type exists
    ds_config = get_dataset_type(dataset_type)
    if ds_config is None:
        available = [ds.name for ds in get_all_dataset_types()]
        logger.warning(f"Dataset type '{dataset_type}' not found. Available: {', '.join(available)}")
        raise HTTPException(
            status_code=404,
            detail=f"Dataset type '{dataset_type}' not found. Available types: {', '.join(available)}",
        )

    # Get metadata, optionally filtered by scope
    if scope:
        fields_metadata = get_fields_metadata_by_scope(scope, dataset_type)
        if fields_metadata is None:
            from peskas_api.schema.scopes import get_available_scopes

            available_scopes = get_available_scopes(dataset_type)
            logger.warning(
                f"Invalid scope '{scope}' for dataset type '{dataset_type}'. "
                f"Available scopes: {', '.join(available_scopes)}"
            )
            raise HTTPException(
                status_code=400,
                detail=f"Invalid scope '{scope}' for dataset type '{dataset_type}'. Available scopes: {', '.join(available_scopes)}",
            )
        logger.info(f"Retrieved metadata for {len(fields_metadata)} fields in scope '{scope}' for dataset '{dataset_type}'")
    else:
        fields_metadata = get_all_fields_metadata(dataset_type)
        logger.info(f"Retrieved metadata for {len(fields_metadata)} fields for dataset '{dataset_type}'")

    # Convert FieldMetadata dataclasses to Pydantic models
    field_responses = {
        field_name: FieldMetadataResponse(
            name=metadata.name,
            description=metadata.description,
            data_type=metadata.data_type,
            unit=metadata.unit,
            possible_values=metadata.possible_values,
            value_range=list(metadata.value_range) if metadata.value_range else None,
            examples=metadata.examples,
            required=metadata.required,
            ontology_url=metadata.ontology_url,
        )
        for field_name, metadata in fields_metadata.items()
    }

    return DatasetMetadataResponse(
        dataset_type=dataset_type,
        fields=field_responses,
    )


@router.get(
    "/metadata/{dataset_type}/fields/{field_name}",
    response_model=FieldMetadataResponse,
    summary="Get single field metadata",
    description="Get detailed metadata for a specific field in a dataset type.",
)
async def get_field_metadata_endpoint(
    dataset_type: str,
    field_name: str,
    _auth: AuthenticatedUser = Depends(),
):
    """
    Get metadata for a specific field.

    Args:
        dataset_type: Dataset type name (e.g., 'landings')
        field_name: Name of the field/column

    Returns:
        FieldMetadataResponse with field metadata

    Raises:
        401: If API key is missing or invalid
        404: If dataset type or field not found
    """
    # Validate dataset type exists
    ds_config = get_dataset_type(dataset_type)
    if ds_config is None:
        available = [ds.name for ds in get_all_dataset_types()]
        logger.warning(f"Dataset type '{dataset_type}' not found. Available: {', '.join(available)}")
        raise HTTPException(
            status_code=404,
            detail=f"Dataset type '{dataset_type}' not found. Available types: {', '.join(available)}",
        )

    # Get field metadata
    metadata = get_field_metadata(field_name, dataset_type)
    if metadata is None:
        all_fields = get_all_fields_metadata(dataset_type)
        available_fields = list(all_fields.keys())
        logger.warning(
            f"Field '{field_name}' not found in dataset type '{dataset_type}'. "
            f"Available fields: {', '.join(available_fields[:10])}{'...' if len(available_fields) > 10 else ''}"
        )
        raise HTTPException(
            status_code=404,
            detail=f"Field '{field_name}' not found in dataset type '{dataset_type}'. Available fields: {', '.join(available_fields)}",
        )

    logger.info(f"Retrieved metadata for field '{field_name}' in dataset '{dataset_type}'")

    return FieldMetadataResponse(
        name=metadata.name,
        description=metadata.description,
        data_type=metadata.data_type,
        unit=metadata.unit,
        possible_values=metadata.possible_values,
        value_range=list(metadata.value_range) if metadata.value_range else None,
        examples=metadata.examples,
        required=metadata.required,
        ontology_url=metadata.ontology_url,
    )
