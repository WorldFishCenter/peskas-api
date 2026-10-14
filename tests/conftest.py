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
            "survey_organization": ["ZAFIRI", "ZAFIRI", "ZAFIRI"],
            "survey_id": ["survey_1", "survey_1", "survey_2"],
            "trip_id": ["trip_1", "trip_2", "trip_3"],
            "landing_date": pd.to_datetime(["2025-01-15", "2025-02-10", "2025-02-28"]).date,  # DATE, as the pipelines write it
            "gaul_1_code": ["1696", "1696", "1697"],
            "gaul_1_name": ["Unguja North", "Unguja North", "Pemba North"],
            "gaul_2_code": ["16961", "16961", "16971"],
            "gaul_2_name": ["District A", "District A", "District B"],
            "landing_site": ["Nungwi", "Mkokotoni", "Mazizini"],
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
def test_district_months_parquet(tmp_path: Path) -> Path:
    """Two districts over two months, in the column order peskas.coasts writes."""
    from peskas_api.schema.field_metadata import FIELD_METADATA

    df = pd.DataFrame(
        {
            "country": "zanzibar",
            "month": pd.to_datetime(["2026-02-01", "2026-03-01", "2026-03-01"]).date,
            "gaul_1_code": ["1691", "1691", "1690"],
            "gaul_1_name": ["Kusini Unguja", "Kusini Unguja", "Kusini Pemba"],
            "gaul_2_code": ["106434", "106434", "106432"],
            "gaul_2_name": ["Kati", "Kati", "Chake Chake"],
            "n_submissions": [0, 74, 36],
        }
    )
    for column in list(FIELD_METADATA["district-months"])[7:]:
        df[column] = [None, 1.5, 2.5]

    parquet_path = tmp_path / "district-months.parquet"
    df.to_parquet(parquet_path)
    return parquet_path


@pytest.fixture
def mock_gcs_service(test_parquet: Path, test_district_months_parquet: Path):
    """Mock GCS service that returns each dataset's test parquet."""
    from peskas_api.services.gcs import GCSService

    files = {"landings": test_parquet, "district-months": test_district_months_parquet}
    mock = MagicMock(spec=GCSService)
    mock.download_parquet.side_effect = lambda country, status=None, dataset="landings": files[dataset]
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
