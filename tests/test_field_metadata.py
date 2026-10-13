"""Field metadata and scope integration tests."""

from peskas_api.schema.field_metadata import get_field_metadata
from peskas_api.schema.scopes import get_scope_columns


def test_landing_site_metadata():
    """landing_site should have AQFO ontology metadata."""
    metadata = get_field_metadata("landing_site")
    assert metadata is not None
    assert metadata.name == "landing_site"
    assert metadata.data_type == "string"
    assert metadata.ontology_url == "http://w3id.org/aqfo/aqfo_00000030"
    assert "land their catch" in metadata.description


def test_landing_site_in_trip_info_scope():
    """landing_site should be included in the trip_info scope."""
    columns = get_scope_columns("trip_info")
    assert columns is not None
    assert "landing_site" in columns


def test_survey_organization_metadata():
    """survey_organization should list the collecting organizations."""
    metadata = get_field_metadata("survey_organization")
    assert metadata is not None
    assert metadata.data_type == "string"
    assert metadata.possible_values == ["KEFS", "WCS", "ZAFIRI", "MAF", "DINAPA"]


def test_survey_organization_in_trip_info_scope():
    """survey_organization should be included in the trip_info scope."""
    columns = get_scope_columns("trip_info")
    assert columns is not None
    assert "survey_organization" in columns


def test_district_months_fields_match_the_coasts_file():
    """The 23 columns peskas.coasts writes (tests/testthat/test-api-district-months.R)."""
    from peskas_api.schema.field_metadata import get_all_fields_metadata

    assert list(get_all_fields_metadata("district-months")) == [
        "country", "month", "gaul_1_code", "gaul_1_name", "gaul_2_code", "gaul_2_name",
        "n_submissions", "mean_n_fishers", "mean_trip_duration_hrs", "mean_catch_kg",
        "mean_catch_price", "mean_price_kg", "mean_cpue", "mean_rpue",
        "estimated_fishing_trips", "estimated_catch_tn", "estimated_revenue", "sampling_rate",
        "estimated_fishing_trips_fao", "estimated_catch_tn_fao", "estimated_revenue_fao",
        "relative_error_catch_fao", "relative_error_revenue_fao",
    ]


def test_latest_file_is_found_per_dataset(monkeypatch):
    """Each dataset reads only its own versioned files, newest first."""
    from unittest.mock import MagicMock

    from peskas_api.schema.dataset_config import get_dataset_type
    from peskas_api.services.gcs import GCSService

    names = [
        "zanzibar/aggregated/district-months__20261013093008_ca7636f__.parquet",
        "zanzibar/aggregated/district-months__20261012093008_ca7636f__.parquet",
        "zanzibar/aggregated/trips-validated__20261014093008_ca7636f__.parquet",
    ]
    bucket = MagicMock()
    bucket.list_blobs.return_value = [MagicMock(name=n) for n in names]
    for blob, n in zip(bucket.list_blobs.return_value, names):
        blob.name = n
    monkeypatch.setattr(GCSService, "bucket", property(lambda self: bucket))

    gcs = GCSService()
    pattern = get_dataset_type("district-months").file_pattern
    assert gcs._get_latest_file("zanzibar/aggregated/", pattern) == names[0]
    assert gcs.build_object_path("Zanzibar", "aggregated") == "zanzibar/aggregated/"
