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
    value_range: tuple[float | None, float | None] | None = (
        None  # (min, max) for numeric ranges
    )
    examples: list[Any] | None = None
    required: bool = False
    ontology_url: str | None = (
        None  # URL to formal ontology definition (e.g., AQFO, schema.org)
    )
    url: str | None = (
        None  # URL to reference documentation (e.g., FAO ASFIS catalog, GAUL dataset)
    )


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
            unit="ISO 8601 date format (YYYY-MM-DD)",
            data_type="date",
            examples=["2025-02-19", "2024-02-19"],
        ),
        # Geographic identifiers
        "gaul_1_code": FieldMetadata(
            name="gaul_1_code",
            description="GAUL (Global Administrative Unit Layers) level 1 administrative code. The administrative boundaries at the level 1 dataset distinguishes States, Provinces, Departments and equivalent",
            data_type="string",
            examples=["1696", "1697"],
            url="https://data.apps.fao.org/catalog/dataset/34f97afc-6218-459a-971d-5af1162d318a/resource/d472b55c-a1e0-4c9c-9ccb-8bf10c8bf0a3",  # GAUL ontology
        ),
        "gaul_1_name": FieldMetadata(
            name="gaul_1_name",
            description="Human-readable name of the GAUL level 1 administrative unit",
            data_type="string",
            examples=["Unguja North", "Pemba North", "Unguja South"],
            url="https://data.apps.fao.org/catalog/dataset/34f97afc-6218-459a-971d-5af1162d318a/resource/d472b55c-a1e0-4c9c-9ccb-8bf10c8bf0a3",  # GAUL ontology
        ),
        "gaul_2_code": FieldMetadata(
            name="gaul_2_code",
            description="GAUL (Global Administrative Unit Layers) level 2 administrative code. The administrative boundaries at the level 2 dataset distinguishes Districts and equivalent",
            data_type="string",
            examples=["16961", "16971"],
            url="https://data.apps.fao.org/catalog/dataset/60b23906-f21a-49ef-8424-f3645e70264e/resource/a4d23085-c6be-4924-b4be-1df45cec4168",  # GAUL ontology
        ),
        "gaul_2_name": FieldMetadata(
            name="gaul_2_name",
            description="Human-readable name of the GAUL level 2 administrative unit",
            data_type="string",
            examples=["District A", "District B"],
            url="https://data.apps.fao.org/catalog/dataset/60b23906-f21a-49ef-8424-f3645e70264e/resource/a4d23085-c6be-4924-b4be-1df45cec4168",  # GAUL ontology
        ),
        # Trip characteristics
        "n_fishers": FieldMetadata(
            name="n_fishers",
            description="The total number of people actively fishing on a fishing trip",
            data_type="integer",
            value_range=(1, None),
            examples=[1, 2, 3, 4, 5],
            ontology_url="http://w3id.org/aqfo/aqfo_00000022",
        ),
        "trip_duration_hrs": FieldMetadata(
            name="trip_duration_hrs",
            description="Refers to the duration of fishing, measured in time (normally days or hours) between departure and return time and date.",
            data_type="float",
            unit="hours",
            value_range=(0.0, None),
            examples=[4.5, 6.0, 8.5, 12.0],
            ontology_url="http://w3id.org/aqfo/aqfo_00002011",
        ),
        "gear": FieldMetadata(
            name="gear",
            description="A fishing gear is a tool or method used to catch fish, such as hook-and-line, trawl net, gillnet, pot, trap, spear, manual collection etc.",
            data_type="string",
            possible_values=["hand_line", "net", "trap", "spear", "longline", "trawl"],
            examples=["hand_line", "net", "trap"],
            ontology_url="http://w3id.org/aqfo/aqfo_00002220",
        ),
        "vessel_type": FieldMetadata(
            name="vessel_type",
            description="Refers to any water vehicle that operates above or under the water surface with or without an engine or other form of propulsion.",
            data_type="string",
            possible_values=[
                "outrigger",
                "dhow",
                "canoe",
            ],
            examples=["outrigger", "dhow", "canoe"],
            ontology_url="http://w3id.org/aqfo/aqfo_00001013",
        ),
        "catch_habitat": FieldMetadata(
            name="catch_habitat",
            description="The place where an organism lives or the place one would go to find it. The habitat is the organisms address, and the ecological niche its profession, biologically speaking.",
            data_type="string",
            possible_values=["reef", "pelagic", "demersal", "coastal", "offshore"],
            examples=["reef", "pelagic", "mangroves"],
            ontology_url="http://w3id.org/aqfo/aqfo_00000023",
        ),
        "catch_outcome": FieldMetadata(
            name="catch_outcome",
            description=(
                "Binary indicator of whether the fishing trip resulted in any catch. "
                "Use 1 for a positive outcome (at least one catch recorded), 0 for no catch."
            ),
            data_type="integer",
            possible_values=["0", "1"],
            examples=[1, 0],
        ),
        # Catch characteristics
        "n_catch": FieldMetadata(
            name="n_catch",
            description=(
                "Number of distinct catch records reported for the trip. A catch record is defined by a unique "
                "combination of taxon (e.g., FAO ASFIS code) and size/length class. For example, two tunas in "
                "different length classes (e.g., 10–15 cm and 20–25 cm) count as two catches."
            ),
            data_type="integer",
            value_range=(0, None),
            examples=[0, 1, 3, 10],
        ),
        "catch_taxon": FieldMetadata(
            name="catch_taxon",
            description="3-alpha code identifying the species or taxonomic group according to the FAO ASFIS List of Species for Fishery Statistics Purposes",
            data_type="string",
            possible_values=[
                "MZZ",
                "SKJ",
                "IAX",
                "TUN",
                "YFT",
                "BET",
            ],  # Common examples
            examples=["MZZ", "SKJ", "IAX"],
            url="https://www.fao.org/fishery/en/collection/asfis",
        ),
        "length_cm": FieldMetadata(
            name="length_cm",
            description=(
                "Length class associated with the catch record. Although stored as a numeric value, for fish up to 100 cm "
                "this field represents membership in predefined length ranges used in data collection: <10, 10–15, 15–20, "
                "20–25, 25–30, 30–40, 40–50, 50–60, 60–70, 70–80, 80–90, 90–100 cm. For fish larger than 1 meter, the "
                "enumerator records the measured length in cm (e.g., 110, 130, 145, 200) rather than a range label."
            ),
            data_type="float",
            unit="cm",
            value_range=(0.0, None),
            examples=[10.0, 15.0, 30.0, 90.0, 110.0, 145.0, 200.0],
            ontology_url="http://w3id.org/aqfo/aqfo_00002073",
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
            ontology_url="http://w3id.org/aqfo/aqfo_00002015",
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
