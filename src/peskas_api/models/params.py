"""
Query parameter schemas.

Pydantic models for validating and documenting API parameters.
"""

from datetime import date
from typing import Annotated

from pydantic import BaseModel, Field, field_validator, model_validator

from peskas_api.models.enums import DatasetStatus, ResponseFormat


class DatasetQueryParams(BaseModel):
    """
    Common query parameters for dataset endpoints.

    These parameters apply to all dataset type endpoints.
    """

    country: Annotated[
        str,
        Field(
            min_length=2,
            max_length=50,
            description="Country identifier (e.g., 'zanzibar')",
            examples=["zanzibar"],
        ),
    ]

    status: Annotated[
        DatasetStatus,
        Field(
            default=DatasetStatus.VALIDATED,
            description="Dataset status: 'raw' or 'validated'",
        ),
    ] = DatasetStatus.VALIDATED

    date_from: Annotated[
        date | None,
        Field(
            default=None,
            description="Start date filter (inclusive), format: YYYY-MM-DD",
            examples=["2023-01-01"],
        ),
    ] = None

    date_to: Annotated[
        date | None,
        Field(
            default=None,
            description="End date filter (inclusive), format: YYYY-MM-DD",
            examples=["2023-12-31"],
        ),
    ] = None

    gaul_1: Annotated[
        str | None,
        Field(
            default=None,
            description="GAUL level 1 administrative code filter",
            examples=["1696"],
        ),
    ] = None

    catch_taxon: Annotated[
        str | None,
        Field(
            default=None,
            description="FAO ASFIS species code filter (e.g., 'MZZ', 'SKJ')",
            examples=["MZZ", "SKJ"],
        ),
    ] = None

    fields: Annotated[
        str | None,
        Field(
            default=None,
            description="Comma-separated list of columns to return",
            examples=["trip_id,landing_date,catch_kg"],
        ),
    ] = None

    scope: Annotated[
        str | None,
        Field(
            default=None,
            description="Predefined column scope: 'core', 'detailed', 'summary', 'trip'",
            examples=["core"],
        ),
    ] = None

    limit: Annotated[
        int | None,
        Field(
            default=None,
            ge=1,
            le=1_000_000,
            description="Maximum rows to return",
        ),
    ] = None

    format: Annotated[
        ResponseFormat,
        Field(
            default=ResponseFormat.CSV,
            description="Response format: 'csv' or 'json'",
        ),
    ] = ResponseFormat.CSV

    @field_validator("country")
    @classmethod
    def normalize_country(cls, v: str) -> str:
        """Normalize country identifier to lowercase."""
        return v.lower()

    @model_validator(mode="after")
    def validate_date_range(self) -> "DatasetQueryParams":
        """Ensure date_to >= date_from if both provided."""
        if self.date_from is not None and self.date_to is not None:
            if self.date_to < self.date_from:
                raise ValueError("date_to must be >= date_from")
        return self

    def get_columns(self, dataset_type: str = "landings") -> list[str] | None:
        """
        Resolve columns from fields or scope parameter.

        Priority: fields > scope > None (all columns)
        """
        if self.fields:
            return [f.strip() for f in self.fields.split(",")]

        if self.scope:
            from peskas_api.schema.scopes import get_scope_columns

            return get_scope_columns(self.scope, dataset_type)

        return None
