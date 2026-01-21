"""
Application configuration loaded from environment variables.

All configurable settings are centralized here. Schema-specific settings
(like date column names) are isolated to make future changes easy.
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from peskas_api import __version__


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # === API Configuration ===
    api_title: str = "Peskas Fishery Data API"
    api_version: str = __version__  # Read from package metadata (pyproject.toml)
    api_prefix: str = "/api/v1"
    debug: bool = False

    # === Authentication ===
    api_secret_key: str = Field(..., description="Shared secret for X-API-Key header")
    api_key_header_name: str = "X-API-Key"

    # === GCS Configuration ===
    gcs_bucket_name: str = Field(..., description="GCS bucket containing parquet files")
    gcs_project_id: str | None = None

    # === Data Layout ===
    # Pattern: {country}/{status}/ (files are versioned within folder)
    # Example: zanzibar/raw/trips-raw__20260120143613_7c6156d__.parquet
    gcs_path_template: str = "{country}/{status}/"

    # Filename pattern for versioned parquet files
    # Pattern: trips-{status}__{YYYYMMDDHHMMSS}_{hash}__.parquet
    gcs_filename_pattern: str = r'trips-\w+__(\d{14})_[a-f0-9]+__.parquet'

    # === Schema Configuration ===
    default_date_column: str = "landing_date"
    default_status: Literal["raw", "validated"] = "validated"

    # === Query Limits ===
    max_rows_default: int = 100_000
    max_rows_limit: int = 1_000_000

    # === Temporary Storage ===
    temp_dir: str = "/tmp/peskas_cache"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
