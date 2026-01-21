"""
Pytest fixtures for testing.
"""

import os
from pathlib import Path
from unittest.mock import MagicMock

import pandas as pd
import pytest
from fastapi.testclient import TestClient

# Set test environment variables before importing app
os.environ["API_SECRET_KEY"] = "test-secret-key"
os.environ["GCS_BUCKET_NAME"] = "test-bucket"


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
def client(mock_gcs_service):
    """Test client with mocked services."""
    from peskas_api.main import app
    from peskas_api.services.gcs import get_gcs_service

    app.dependency_overrides[get_gcs_service] = lambda: mock_gcs_service

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers():
    """Valid auth headers."""
    return {"X-API-Key": "test-secret-key"}
