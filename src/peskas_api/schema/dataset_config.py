"""
Dataset type configuration.

This module centralizes all dataset type definitions. When new dataset
types are added or names change, only this file needs updating.
"""

from dataclasses import dataclass


@dataclass
class DatasetType:
    """Configuration for a dataset type."""

    name: str  # Internal name (used in GCS paths)
    endpoint: str  # API endpoint path segment
    description: str  # Human-readable description
    date_column: str  # Column to use for date filtering


# === Dataset Type Registry ===
# Add new dataset types here. The API router will automatically
# pick them up and create endpoints.
#
# Note: Trip data is included in the landings dataset (wide format)
# so there is only one dataset type.

DATASET_TYPES: dict[str, DatasetType] = {
    "landings": DatasetType(
        name="landings",
        endpoint="landings",
        description="Fish landing records with catch and trip information",
        date_column="landing_date",
    ),
}


def get_dataset_type(name: str) -> DatasetType | None:
    """Get dataset type by name."""
    return DATASET_TYPES.get(name)


def get_all_dataset_types() -> list[DatasetType]:
    """Get all registered dataset types."""
    return list(DATASET_TYPES.values())
