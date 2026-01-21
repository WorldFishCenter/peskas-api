"""Enumerations for API parameters."""

from enum import Enum


class DatasetStatus(str, Enum):
    """Dataset processing status."""

    RAW = "raw"
    VALIDATED = "validated"


class ResponseFormat(str, Enum):
    """Response format options."""

    CSV = "csv"
    JSON = "json"
