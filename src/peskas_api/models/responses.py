"""Response schemas."""

from typing import Any, Literal

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


class FieldMetadataResponse(BaseModel):
    """Metadata for a single field."""

    name: str = Field(description="Field/column name")
    description: str = Field(description="Human-readable description of the field")
    data_type: str = Field(
        description="Data type: 'string', 'integer', 'float', 'date', or 'datetime'"
    )
    unit: str | None = Field(
        default=None,
        description="Unit of measurement (e.g., 'kg', 'cm', 'hours')"
    )
    possible_values: list[str] | None = Field(
        default=None,
        description="List of possible values for categorical/enum fields"
    )
    value_range: list[float | None] | None = Field(
        default=None,
        description="Minimum and maximum values for numeric fields as [min, max] (null indicates unbounded)"
    )
    examples: list[Any] | None = Field(
        default=None,
        description="Example values for this field"
    )
    required: bool = Field(
        default=False,
        description="Whether this field is required"
    )
    ontology_url: str | None = Field(
        default=None,
        description="URL to the ontology definition for this field (e.g., FAO ASFIS, GAUL, schema.org). Enables semantic web interoperability and machine-readable field definitions."
    )


class DatasetMetadataResponse(BaseModel):
    """Metadata for a dataset type."""

    dataset_type: str = Field(description="Dataset type name (e.g., 'landings')")
    fields: dict[str, FieldMetadataResponse] = Field(
        description="Dictionary mapping field names to their metadata"
    )


class MetadataListResponse(BaseModel):
    """List of available dataset types with metadata."""

    dataset_types: list[str] = Field(
        description="List of available dataset type names"
    )
