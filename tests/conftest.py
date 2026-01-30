"""
Pytest fixtures for testing.
"""

import os
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pandas as pd
import pytest
import yaml
from fastapi.testclient import TestClient

# Set test environment variables before importing app
os.environ["GCS_BUCKET_NAME"] = "test-bucket"
os.environ["MONGO_URI"] = "mongodb://localhost:27017"  # Will be mocked


@pytest.fixture
def test_api_keys_config(tmp_path: Path) -> Path:
    """Create a test API keys configuration file."""
    config_data = {
        "api_keys": {
            "test-admin-key": {
                "name": "Test Admin Key",
                "description": "Full access for testing",
                "enabled": True,
                "permissions": {
                    "allow_all": True
                }
            },
            "test-restricted-key": {
                "name": "Test Restricted Key",
                "description": "Country-restricted key for testing",
                "enabled": True,
                "permissions": {
                    "countries": ["zanzibar"]
                }
            },
            "test-date-restricted-key": {
                "name": "Test Date Restricted Key",
                "description": "Date-restricted key for testing",
                "enabled": True,
                "permissions": {
                    "date_from": "2025-01-01",
                    "date_to": "2025-12-31"
                }
            },
            "test-disabled-key": {
                "name": "Test Disabled Key",
                "description": "Disabled key for testing",
                "enabled": False,
                "permissions": {
                    "allow_all": False
                }
            }
        }
    }

    config_path = tmp_path / "test_api_keys.yaml"
    with open(config_path, "w") as f:
        yaml.dump(config_data, f)

    return config_path


@pytest.fixture
def mock_audit_service():
    """Mock audit service with in-memory storage."""
    mock = AsyncMock()
    # Make all audit logging methods succeed silently
    mock.log_auth_success = AsyncMock()
    mock.log_auth_failure = AsyncMock()
    mock.log_permission_check = AsyncMock()
    mock.log_data_access = AsyncMock()
    return mock


@pytest.fixture
def test_parquet(tmp_path: Path) -> Path:
    """Create a test parquet file with actual 18-column schema."""
    df = pd.DataFrame(
        {
            "survey_id": ["survey_1", "survey_1", "survey_2"],
            "trip_id": ["trip_1", "trip_2", "trip_3"],
            "landing_date": pd.to_datetime(["2025-01-15", "2025-02-10", "2025-02-28"]),
            "gaul_1_code": ["1696", "1696", "1697"],
            "gaul_1_name": ["Unguja North", "Unguja North", "Pemba North"],
            "gaul_2_code": ["16961", "16961", "16971"],
            "gaul_2_name": ["District A", "District A", "District B"],
            "n_fishers": [3, 2, 4],
            "trip_duration_hrs": [4.5, 6.0, 3.5],
            "gear": ["hand_line", "net", "trap"],
            "vessel_type": ["outrigger", "dhow", "outrigger"],
            "catch_habitat": ["reef", "pelagic", "reef"],
            "catch_outcome": ["kept", "kept", "released"],
            "n_catch": [10, 25, 8],
            "catch_taxon": ["MZZ", "SKJ", "IAX"],
            "length_cm": [25.5, 45.0, 30.0],
            "catch_kg": [15.5, 120.0, 8.5],
            "catch_price": [50000, 200000, 30000],
        }
    )

    parquet_path = tmp_path / "test.parquet"
    df.to_parquet(parquet_path)
    return parquet_path


@pytest.fixture
def mock_gcs_service(test_parquet: Path):
    """Mock GCS service that returns test parquet."""
    from peskas_api.services.gcs import GCSService

    mock = MagicMock(spec=GCSService)
    mock.download_parquet.return_value = test_parquet
    return mock


@pytest.fixture
def client(mock_gcs_service, test_api_keys_config, mock_audit_service):
    """Test client with mocked services and test API keys."""
    # Set test API keys config path
    os.environ["API_KEYS_CONFIG_PATH"] = str(test_api_keys_config)

    # Clear LRU cache to force reload with test config
    from peskas_api.services.api_keys import get_api_key_service
    from peskas_api.services.audit import get_audit_service
    get_api_key_service.cache_clear()
    get_audit_service.cache_clear()

    from peskas_api.main import app
    from peskas_api.services.gcs import get_gcs_service

    app.dependency_overrides[get_gcs_service] = lambda: mock_gcs_service
    app.dependency_overrides[get_audit_service] = lambda: mock_audit_service

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    get_api_key_service.cache_clear()
    get_audit_service.cache_clear()


@pytest.fixture
def auth_headers():
    """Valid auth headers with admin key."""
    return {"X-API-Key": "test-admin-key"}


@pytest.fixture
def restricted_auth_headers():
    """Valid auth headers with restricted key (zanzibar only)."""
    return {"X-API-Key": "test-restricted-key"}
