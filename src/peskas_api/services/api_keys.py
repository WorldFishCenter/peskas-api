"""
API key registry service.

Loads and manages API key configurations from YAML file.
"""

import logging
import os
from functools import lru_cache
from pathlib import Path

import yaml
from pydantic import ValidationError

from peskas_api.models.permissions import APIKeyRegistry, APIKeyConfig

logger = logging.getLogger(__name__)


class APIKeyService:
    """Service for managing API key registry."""

    def __init__(self, config_path: str | Path):
        """
        Initialize API key service.

        Args:
            config_path: Path to api_keys.yaml file
        """
        self.config_path = Path(config_path)
        self._registry: APIKeyRegistry | None = None
        self._load_registry()

    def _load_registry(self) -> None:
        """Load API key registry from YAML file."""
        try:
            if not self.config_path.exists():
                logger.warning(
                    f"API keys config file not found: {self.config_path}. "
                    "Using empty registry."
                )
                self._registry = APIKeyRegistry(api_keys={})
                return

            with open(self.config_path, "r") as f:
                data = yaml.safe_load(f)

            if not data:
                logger.warning("API keys config file is empty")
                self._registry = APIKeyRegistry(api_keys={})
                return

            self._registry = APIKeyRegistry(**data)
            logger.info(
                f"Loaded {len(self._registry.api_keys)} API keys from {self.config_path}"
            )

        except ValidationError as e:
            logger.error(f"Invalid API keys configuration: {e}")
            raise ValueError(f"Invalid API keys configuration: {e}")
        except Exception as e:
            logger.error(f"Failed to load API keys: {e}")
            raise

    def get_key_config(self, api_key: str) -> APIKeyConfig | None:
        """
        Get configuration for an API key.

        Args:
            api_key: The API key string

        Returns:
            APIKeyConfig if key exists, None otherwise
        """
        if self._registry is None:
            return None
        return self._registry.get_key_config(api_key)

    def is_valid_key(self, api_key: str) -> bool:
        """
        Check if API key is valid and enabled.

        Args:
            api_key: The API key string

        Returns:
            True if key is valid and enabled
        """
        if self._registry is None:
            return False
        return self._registry.is_valid_key(api_key)

    def reload(self) -> None:
        """Reload the API key registry from disk."""
        logger.info("Reloading API key registry")
        self._load_registry()


@lru_cache
def get_api_key_service() -> APIKeyService:
    """
    Get cached API key service instance.

    Returns:
        Singleton APIKeyService instance
    """
    # Look for api_keys.yaml in project root
    # Configuration path can be overridden via environment variable
    config_path = os.environ.get(
        "API_KEYS_CONFIG_PATH",
        "api_keys.yaml"
    )
    return APIKeyService(config_path)
