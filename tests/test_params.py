"""Query parameter validation tests."""

from datetime import date

import pytest

from peskas_api.models.params import DatasetQueryParams
from peskas_api.models.enums import DatasetStatus


def test_valid_params():
    """Valid parameters should parse correctly."""
    params = DatasetQueryParams(
        country="Zanzibar",
        status=DatasetStatus.VALIDATED,
    )
    assert params.country == "zanzibar"  # Normalized to lowercase
    assert params.status == DatasetStatus.VALIDATED


def test_date_range_validation():
    """date_to < date_from should fail."""
    with pytest.raises(ValueError):
        DatasetQueryParams(
            country="zanzibar",
            date_from=date(2025, 6, 1),
            date_to=date(2025, 1, 1),
        )


def test_valid_date_range():
    """Valid date range should pass."""
    params = DatasetQueryParams(
        country="zanzibar",
        date_from=date(2025, 1, 1),
        date_to=date(2025, 6, 1),
    )
    assert params.date_from == date(2025, 1, 1)
    assert params.date_to == date(2025, 6, 1)


def test_fields_parsing():
    """Fields parameter should parse to column list."""
    params = DatasetQueryParams(
        country="zanzibar",
        fields="trip_id, landing_date, catch_kg",
    )
    columns = params.get_columns()
    assert columns == ["trip_id", "landing_date", "catch_kg"]


def test_default_status():
    """Default status should be validated."""
    params = DatasetQueryParams(country="zanzibar")
    assert params.status == DatasetStatus.VALIDATED


def test_gaul_1_filter():
    """GAUL level 1 filter should be optional."""
    params = DatasetQueryParams(
        country="zanzibar",
        gaul_1="1696",
    )
    assert params.gaul_1 == "1696"


def test_catch_taxon_filter():
    """Catch taxon filter should be optional."""
    params = DatasetQueryParams(
        country="zanzibar",
        catch_taxon="MZZ",
    )
    assert params.catch_taxon == "MZZ"


def test_combined_filters():
    """Multiple filters should work together."""
    params = DatasetQueryParams(
        country="zanzibar",
        gaul_1="1696",
        catch_taxon="SKJ",
        date_from=date(2025, 1, 1),
        date_to=date(2025, 2, 28),
    )
    assert params.gaul_1 == "1696"
    assert params.catch_taxon == "SKJ"
    assert params.date_from == date(2025, 1, 1)
    assert params.date_to == date(2025, 2, 28)
