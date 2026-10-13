"""
Dataset type configuration.

This module centralizes all dataset type definitions. When new dataset
types are added or names change, only this file needs updating.
"""

from dataclasses import dataclass


@dataclass
class DatasetType:
    """Configuration for a dataset type."""

    name: str  # Internal name (also the /metadata/{name} path)
    endpoint: str  # API endpoint path segment
    description: str  # Human-readable description
    date_column: str  # Column to use for date filtering
    folder: str  # GCS folder under {country}/; "{status}" is replaced by raw/validated
    file_pattern: str  # Versioned filename regex; group 1 is the YYYYMMDDHHMMSS timestamp


# === Dataset Type Registry ===
# Each dataset's endpoint is registered in api/endpoints/datasets.py; the
# /metadata endpoints list every type here.
#
# Note: Trip data is included in the landings dataset (wide format).

DATASET_TYPES: dict[str, DatasetType] = {
    "landings": DatasetType(
        name="landings",
        endpoint="landings",
        description="Fish landing records with catch and trip information",
        date_column="landing_date",
        folder="{status}",
        file_pattern=r"trips-\w+__(\d{14})_[a-f0-9]+__.parquet",
    ),
    # Written by peskas.coasts export_portal() (api_district_months()).
    "district-months": DatasetType(
        name="district-months",
        endpoint="district-months",
        description="Monthly figures per district: recorded averages and whole-fleet estimates",
        date_column="month",
        folder="aggregated",
        file_pattern=r"district-months__(\d{14})_[a-f0-9]+__.parquet",
    ),
}


def get_dataset_type(name: str) -> DatasetType | None:
    """Get dataset type by name."""
    return DATASET_TYPES.get(name)


def get_all_dataset_types() -> list[DatasetType]:
    """Get all registered dataset types."""
    return list(DATASET_TYPES.values())
