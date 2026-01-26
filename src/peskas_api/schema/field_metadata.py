"""
Field metadata definitions.

This module centralizes all field/column metadata including descriptions,
data types, units, possible values, and examples. This metadata is used
for API documentation and the metadata endpoint.

To add or modify field metadata, update the FIELD_METADATA dictionary below.
Each dataset type can have its own set of field definitions.
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class FieldMetadata:
    """Metadata for a single data field/column.
    
    This follows semantic web and FAIR data principles by including
    ontology URLs for machine-readable, interoperable field definitions.
    """

    name: str
    description: str
    data_type: str  # "string", "integer", "float", "date", "datetime"
    unit: str | None = None  # e.g., "kg", "cm", "hours"
    possible_values: list[str] | None = None  # For enum/categorical fields
    value_range: tuple[float | None, float | None] | None = None  # (min, max) for numeric ranges
    examples: list[Any] | None = None
    required: bool = False
    ontology_url: str | None = None  # URL to ontology definition (e.g., FAO ASFIS, GAUL, schema.org)


# Field metadata per dataset type
# Format: {dataset_type: {field_name: FieldMetadata}}
#
# To add a new field, add it to the appropriate dataset type dictionary.
# To add metadata for a new dataset type, create a new entry in FIELD_METADATA.

FIELD_METADATA: dict[str, dict[str, FieldMetadata]] = {
    "landings": {
        # Trip-level identifiers
        "survey_id": FieldMetadata(
            name="survey_id",
            description="Unique identifier for the survey from which this record was collected",
            data_type="string",
            examples=["survey_1", "survey_2", "survey_001"],
        ),
        "trip_id": FieldMetadata(
            name="trip_id",
            description="Unique identifier for the fishing trip",
            data_type="string",
            examples=["trip_1", "trip_2", "trip_001"],
        ),
        "landing_date": FieldMetadata(
            name="landing_date",
            description="Date when the catch was landed (brought to shore)",
            data_type="datetime",
            examples=["2025-01-15T00:00:00", "2025-02-10T00:00:00"],
            ontology_url="https://schema.org/Date",  # Schema.org date type
        ),
        # Geographic identifiers
        "gaul_1_code": FieldMetadata(
            name="gaul_1_code",
            description="GAUL (Global Administrative Unit Layers) level 1 administrative code. Level 1 typically represents the first administrative division (e.g., state, province, region)",
            data_type="string",
            examples=["1696", "1697"],
            ontology_url="https://data.apps.fao.org/map/catalog/srv/eng/catalog.search#/metadata/126831e0-88fd-11da-a88f-000d939bc5d8",  # GAUL ontology
        ),
        "gaul_1_name": FieldMetadata(
            name="gaul_1_name",
            description="Human-readable name of the GAUL level 1 administrative unit",
            data_type="string",
            examples=["Unguja North", "Pemba North", "Unguja South"],
        ),
        "gaul_2_code": FieldMetadata(
            name="gaul_2_code",
            description="GAUL (Global Administrative Unit Layers) level 2 administrative code. Level 2 typically represents the second administrative division (e.g., district, county)",
            data_type="string",
            examples=["16961", "16971"],
        ),
        "gaul_2_name": FieldMetadata(
            name="gaul_2_name",
            description="Human-readable name of the GAUL level 2 administrative unit",
            data_type="string",
            examples=["District A", "District B"],
        ),
        # Trip characteristics
        "n_fishers": FieldMetadata(
            name="n_fishers",
            description="Number of fishers participating in the trip",
            data_type="integer",
            value_range=(1, None),
            examples=[1, 2, 3, 4, 5],
        ),
        "trip_duration_hrs": FieldMetadata(
            name="trip_duration_hrs",
            description="Duration of the fishing trip from departure to return",
            data_type="float",
            unit="hours",
            value_range=(0.0, None),
            examples=[4.5, 6.0, 8.5, 12.0],
        ),
        "gear": FieldMetadata(
            name="gear",
            description="Type of fishing gear used during the trip",
            data_type="string",
            possible_values=["hand_line", "net", "trap", "spear", "longline", "trawl"],
            examples=["hand_line", "net", "trap"],
        ),
        "vessel_type": FieldMetadata(
            name="vessel_type",
            description="Type of vessel used for the fishing trip",
            data_type="string",
            possible_values=["outrigger", "dhow", "canoe", "motorized", "non_motorized"],
            examples=["outrigger", "dhow", "canoe"],
        ),
        "catch_habitat": FieldMetadata(
            name="catch_habitat",
            description="Habitat type where the catch was obtained",
            data_type="string",
            possible_values=["reef", "pelagic", "demersal", "coastal", "offshore"],
            examples=["reef", "pelagic", "demersal"],
        ),
        "catch_outcome": FieldMetadata(
            name="catch_outcome",
            description="Outcome/disposition of the catch",
            data_type="string",
            possible_values=["kept", "released", "discarded", "sold"],
            examples=["kept", "released", "sold"],
        ),
        # Catch characteristics
        "n_catch": FieldMetadata(
            name="n_catch",
            description="Number of individual catch items (fish) in this record",
            data_type="integer",
            value_range=(0, None),
            examples=[1, 10, 25, 50],
        ),
        "catch_taxon": FieldMetadata(
            name="catch_taxon",
            description="FAO ASFIS (Aquatic Sciences and Fisheries Information System) species code. Three-letter code identifying the species or taxonomic group",
            data_type="string",
            possible_values=["MZZ", "SKJ", "IAX", "TUN", "YFT", "BET"],  # Common examples
            examples=["MZZ", "SKJ", "IAX"],
            ontology_url="https://www.fao.org/fishery/collection/asfis/en",  # FAO ASFIS ontology
        ),
        "length_cm": FieldMetadata(
            name="length_cm",
            description="Length of the fish or catch item. Measurement method may vary (total length, fork length, etc.)",
            data_type="float",
            unit="cm",
            value_range=(0.0, None),
            examples=[25.5, 30.0, 45.0, 60.0],
        ),
        "catch_kg": FieldMetadata(
            name="catch_kg",
            description="Weight of the catch in kilograms",
            data_type="float",
            unit="kg",
            value_range=(0.0, None),
            examples=[15.5, 45.2, 120.0, 250.5],
        ),
        "catch_price": FieldMetadata(
            name="catch_price",
            description="Price of the catch in local currency. Currency unit depends on the country",
            data_type="float",
            unit="local_currency",
            value_range=(0.0, None),
            examples=[30000, 50000, 200000],
        ),
    },
}


def get_field_metadata(
    field_name: str,
    dataset_type: str = "landings",
) -> FieldMetadata | None:
    """
    Get metadata for a specific field.

    Args:
        field_name: Name of the field/column
        dataset_type: Dataset type name

    Returns:
        FieldMetadata object, or None if field not found
    """
    type_metadata = FIELD_METADATA.get(dataset_type, {})
    return type_metadata.get(field_name)


def get_all_fields_metadata(
    dataset_type: str = "landings",
) -> dict[str, FieldMetadata]:
    """
    Get metadata for all fields in a dataset type.

    Args:
        dataset_type: Dataset type name

    Returns:
        Dictionary mapping field names to FieldMetadata objects
    """
    return FIELD_METADATA.get(dataset_type, {}).copy()


def get_fields_metadata_by_scope(
    scope: str,
    dataset_type: str = "landings",
) -> dict[str, FieldMetadata] | None:
    """
    Get metadata for fields in a specific scope.

    Args:
        scope: Scope name (e.g., 'trip_info', 'catch_info')
        dataset_type: Dataset type name

    Returns:
        Dictionary mapping field names to FieldMetadata objects, or None if scope not found
    """
    from peskas_api.schema.scopes import get_scope_columns

    columns = get_scope_columns(scope, dataset_type)
    if columns is None:
        return None

    all_metadata = get_all_fields_metadata(dataset_type)
    return {col: all_metadata[col] for col in columns if col in all_metadata}
