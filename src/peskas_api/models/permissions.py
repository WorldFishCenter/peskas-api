"""
Permission models for API key authorization.

Defines the structure of API key permissions and validation logic.
"""

from datetime import date
from typing import Any

from pydantic import BaseModel, Field, field_validator


class APIKeyPermissions(BaseModel):
    """
    Permission rules for an API key.

    All restrictions are optional. If a field is not specified,
    that dimension is unrestricted (unless allow_all is False and
    other restrictions apply).
    """

    allow_all: bool = Field(
        default=False,
        description="If true, this key has full access to all endpoints and data"
    )

    countries: list[str] | None = Field(
        default=None,
        description="Allowed country identifiers. None means all countries allowed."
    )

    statuses: list[str] | None = Field(
        default=None,
        description="Allowed dataset statuses (raw/validated). None means all allowed."
    )

    date_from: date | None = Field(
        default=None,
        description="Minimum date this key can query (inclusive)"
    )

    date_to: date | None = Field(
        default=None,
        description="Maximum date this key can query (inclusive)"
    )

    gaul_1: list[str] | None = Field(
        default=None,
        description="Allowed GAUL level 1 codes. None means all allowed."
    )

    gaul_2: list[str] | None = Field(
        default=None,
        description="Allowed GAUL level 2 codes. None means all allowed."
    )

    catch_taxon: list[str] | None = Field(
        default=None,
        description="Allowed species codes. None means all allowed."
    )

    survey_id: list[str] | None = Field(
        default=None,
        description="Allowed survey IDs. None means all allowed."
    )

    endpoints: list[str] | None = Field(
        default=None,
        description="Allowed endpoint patterns (supports wildcards). None means all allowed."
    )

    max_limit: int | None = Field(
        default=None,
        description="Maximum row limit override for this key"
    )

    @field_validator("countries", "statuses", "gaul_1", "gaul_2", "catch_taxon", "survey_id", mode="before")
    @classmethod
    def normalize_string_lists(cls, v: Any) -> list[str] | None:
        """Normalize string lists to lowercase."""
        if v is None:
            return None
        if isinstance(v, list):
            return [str(item).lower() for item in v]
        return v

    @field_validator("date_from", "date_to", mode="before")
    @classmethod
    def parse_dates(cls, v: Any) -> date | None:
        """Parse date strings to date objects."""
        if v is None:
            return None
        if isinstance(v, date):
            return v
        if isinstance(v, str):
            return date.fromisoformat(v)
        return v


class APIKeyConfig(BaseModel):
    """Configuration for a single API key."""

    name: str = Field(
        description="Human-readable name for this key"
    )

    description: str = Field(
        default="",
        description="Description of the key's purpose"
    )

    permissions: APIKeyPermissions = Field(
        default_factory=APIKeyPermissions,
        description="Permission rules for this key"
    )

    enabled: bool = Field(
        default=True,
        description="Whether this key is currently active"
    )


class APIKeyRegistry(BaseModel):
    """Registry of all API keys and their permissions."""

    api_keys: dict[str, APIKeyConfig] = Field(
        default_factory=dict,
        description="Mapping of API key strings to their configurations"
    )

    def get_key_config(self, api_key: str) -> APIKeyConfig | None:
        """Get configuration for an API key."""
        return self.api_keys.get(api_key)

    def is_valid_key(self, api_key: str) -> bool:
        """Check if a key exists and is enabled."""
        config = self.get_key_config(api_key)
        return config is not None and config.enabled
