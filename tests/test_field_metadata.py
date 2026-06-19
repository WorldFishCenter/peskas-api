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
