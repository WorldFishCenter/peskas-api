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
        "survey_organization": FieldMetadata(
            name="survey_organization",
            description=(
                "Organization that collected the record: KEFS (Kenya Fisheries "
                "Service) and WCS (Wildlife Conservation Society) in Kenya, ZAFIRI "
                "(Zanzibar Fisheries and Marine Resources Research Institute) in "
                "Zanzibar, MAF (Ministry of Agriculture and Fisheries) in Timor-Leste, "
                "and DINAPA (National Directorate of Fisheries and Aquaculture, formerly ADNAP) in "
                "Mozambique. A country can run more "
                "than one survey programme at once, on different instruments: "
                "Kenya publishes WCS and KEFS side by side, and they differ in "
                "what they collect (WCS records no trip duration and no length) "
                "and in how catch is sampled (KEFS weighs the whole catch and "
                "identifies a sample of it, so its catch rows are not meant to "
                "sum to tot_catch_kg). survey_id identifies the form version, "
                "not the organization, so it cannot be used for this."
            ),
            data_type="string",
            possible_values=["KEFS", "WCS", "ZAFIRI", "MAF", "DINAPA"],
            examples=["KEFS", "ZAFIRI"],
        ),
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
        "landing_site": FieldMetadata(
            name="landing_site",
            description=(
                "Location at which boats land their catch. A landing site may be the same as the "
                "homeport or base port but it can also be different. Recording of fishing activities "
                "tend to be conducted in the vessel homeport or base port, while sampling and recording "
                "of catches and species composition, landing prices, etc. are usually undertaken at landing sites."
            ),
            data_type="string",
            examples=["Nungwi", "Mkokotoni", "Mazizini"],
            ontology_url="http://w3id.org/aqfo/aqfo_00000030",
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
        "scientific_name": FieldMetadata(
            name="scientific_name",
            description=(
                "Full binomial scientific name of the species or taxonomic group, "
                "complementing the FAO ASFIS 3-alpha code in catch_taxon "
                "(e.g., 'Katsuwonus pelamis' for SKJ)."
            ),
            data_type="string",
            examples=["Katsuwonus pelamis", "Thunnus albacares", "Thunnus obesus"],
            url="https://www.marinespecies.org",  # World Register of Marine Species (WoRMS)
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
            description=(
                "Price of one catch within a fishing trip, in local currency. "
                "The trip total is `tot_catch_price`. Currency unit depends on the country"
            ),
            data_type="float",
            unit="local_currency",
            value_range=(0.0, None),
            examples=[30000, 50000, 200000],
            ontology_url="http://w3id.org/aqfo/aqfo_00002015",
        ),
        # Trip-level aggregates
        "tot_catch_kg": FieldMetadata(
            name="tot_catch_kg",
            description="Total weight of all catches for the entire fishing trip in kilograms. This is the sum of all catch_kg values for the trip.",
            data_type="float",
            unit="kg",
            value_range=(0.0, None),
            examples=[30.0, 872.0, 26.0, 10.0, 60.0, 70.0],
        ),
        "tot_catch_price": FieldMetadata(
            name="tot_catch_price",
            description="Total price of all catches for the entire fishing trip in local currency. This is the sum of all catch_price values for the trip. Currency unit depends on the country.",
            data_type="float",
            unit="local_currency",
            value_range=(0.0, None),
            examples=[2900, 109, 6500, 1700, 5000, 3200],
        ),
    },
}


# District-months: one row per district and month, written by peskas.coasts
# export_portal() (api_district_months(), whose test pins these 23 columns in
# this order). The GAUL fields are the landings' own.
_ARTFISH_ERROR = (
    "at 90% confidence, as a share of it: 0.44 means within 44%. FAO's OPEN ARTFISH "
    "Toolkit aims for 0.15 or less and accepts up to 0.20. The Toolkit gives this error "
    "for each boat and gear group; the district's adds up theirs, which makes it a "
    "cautious figure. Empty where no group's error can be measured."
)
_TIMOR_MODEL = (
    ". In Timor-Leste, whose rows are municipalities, it comes from the Timor pipeline's "
    "own model instead, and is given for every month from 2018"
)

FIELD_METADATA["district-months"] = {
    "country": FieldMetadata(
        name="country",
        description="Country the row belongs to",
        data_type="string",
        possible_values=["kenya", "mozambique", "timor", "zanzibar"],
        examples=["zanzibar"],
    ),
    "month": FieldMetadata(
        name="month",
        description="Month the landings happened in, as its first day",
        data_type="date",
        unit="ISO 8601 date format (YYYY-MM-DD)",
        examples=["2026-03-01"],
    ),
    **{
        field: FIELD_METADATA["landings"][field]
        for field in ("gaul_1_code", "gaul_1_name", "gaul_2_code", "gaul_2_name")
    },
    "n_submissions": FieldMetadata(
        name="n_submissions",
        description=(
            "Landings (fishing trips) recorded by enumerators in the district that month and "
            "kept after validation. 0 when none were recorded: the row then shows a gap in data "
            "collection, and its other figures are empty. Landings whose site is not matched to "
            "a district are not counted in any row."
        ),
        data_type="integer",
        unit="landings",
        value_range=(0, None),
        examples=[74, 0],
    ),
    "mean_n_fishers": FieldMetadata(
        name="mean_n_fishers",
        description="Average number of fishers on a recorded trip",
        data_type="float",
        unit="fishers",
        value_range=(0.0, None),
        examples=[2.8],
    ),
    "mean_trip_duration_hrs": FieldMetadata(
        name="mean_trip_duration_hrs",
        description="Average duration of a recorded trip. Empty where the survey does not record it",
        data_type="float",
        unit="hours",
        value_range=(0.0, None),
        examples=[5.5],
    ),
    "mean_catch_kg": FieldMetadata(
        name="mean_catch_kg",
        description="Average total catch of a recorded trip",
        data_type="float",
        unit="kg",
        value_range=(0.0, None),
        examples=[14.2],
    ),
    "mean_catch_price": FieldMetadata(
        name="mean_catch_price",
        description="Average value of a recorded trip's catch, in local currency",
        data_type="float",
        unit="local_currency",
        value_range=(0.0, None),
        examples=[85000],
    ),
    "mean_price_kg": FieldMetadata(
        name="mean_price_kg",
        description=(
            "Average price per kilogram: each recorded trip's catch value divided by its catch "
            "weight, averaged over the trips"
        ),
        data_type="float",
        unit="local_currency per kg",
        value_range=(0.0, None),
        examples=[6000],
    ),
    "mean_cpue": FieldMetadata(
        name="mean_cpue",
        description=(
            "Average catch per unit of effort: each recorded trip's catch divided by its fishers "
            "and its hours of fishing, averaged over the trips"
        ),
        data_type="float",
        unit="kg per fisher per hour",
        value_range=(0.0, None),
        examples=[0.92],
    ),
    "mean_rpue": FieldMetadata(
        name="mean_rpue",
        description=(
            "Average revenue per unit of effort: each recorded trip's catch value divided by its "
            "fishers and its hours of fishing, averaged over the trips"
        ),
        data_type="float",
        unit="local_currency per fisher per hour",
        value_range=(0.0, None),
        examples=[5520],
    ),
    "estimated_fishing_trips": FieldMetadata(
        name="estimated_fishing_trips",
        description=(
            "Fishing trips made by all the district's boats that month, by the GPS tracker "
            "method: trips per GPS-tracked boat, scaled up to the boats counted in the census"
            + _TIMOR_MODEL
        ),
        data_type="float",
        unit="trips",
        value_range=(0.0, None),
        examples=[2600],
    ),
    "estimated_catch_tn": FieldMetadata(
        name="estimated_catch_tn",
        description=(
            "Catch landed by all the district's boats that month, by the GPS tracker method: "
            "catch per trip times the estimated trips. Empty when fewer than 10 landings were "
            "recorded" + _TIMOR_MODEL
        ),
        data_type="float",
        unit="tonnes",
        value_range=(0.0, None),
        examples=[36.9],
    ),
    "estimated_revenue": FieldMetadata(
        name="estimated_revenue",
        description=(
            "Value of that catch, in local currency. Empty when fewer than 10 landings were "
            "recorded" + _TIMOR_MODEL
        ),
        data_type="float",
        unit="local_currency",
        value_range=(0.0, None),
        examples=[221000000],
    ),
    "sampling_rate": FieldMetadata(
        name="sampling_rate",
        description=(
            "Share of the district's census boats that carried a GPS tracker that month. It says "
            "how far to trust the GPS tracker estimates: 0.3 or more is good, 0.1 to 0.3 fair, "
            "below 0.1 weak. Empty in Timor-Leste, whose estimates do not use the trackers"
        ),
        data_type="float",
        unit="share",
        value_range=(0.0, None),
        examples=[0.12],
    ),
    "estimated_fishing_trips_fao": FieldMetadata(
        name="estimated_fishing_trips_fao",
        description=(
            "Fishing trips made by all the district's boats that month, by the FAO ARTFISH "
            "method: boats counted in the census times the days they fished, as fishers report "
            "them"
        ),
        data_type="float",
        unit="trips",
        value_range=(0.0, None),
        examples=[2300],
    ),
    "estimated_catch_tn_fao": FieldMetadata(
        name="estimated_catch_tn_fao",
        description=(
            "Catch landed by all the district's boats that month, by the FAO ARTFISH method: "
            "catch per trip times those trips, for each boat and gear group (boat type alone in "
            "Mozambique). Empty when fewer than 10 landings were recorded"
        ),
        data_type="float",
        unit="tonnes",
        value_range=(0.0, None),
        examples=[32.7],
    ),
    "estimated_revenue_fao": FieldMetadata(
        name="estimated_revenue_fao",
        description=(
            "Value of that catch, in local currency. Empty when fewer than 10 landings were "
            "recorded"
        ),
        data_type="float",
        unit="local_currency",
        value_range=(0.0, None),
        examples=[195500000],
    ),
    "relative_error_catch_fao": FieldMetadata(
        name="relative_error_catch_fao",
        description="How far the true catch may differ from estimated_catch_tn_fao, " + _ARTFISH_ERROR,
        data_type="float",
        unit="share",
        value_range=(0.0, None),
        examples=[0.44],
    ),
    "relative_error_revenue_fao": FieldMetadata(
        name="relative_error_revenue_fao",
        description="How far the true revenue may differ from estimated_revenue_fao, " + _ARTFISH_ERROR,
        data_type="float",
        unit="share",
        value_range=(0.0, None),
        examples=[0.42],
    ),
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
