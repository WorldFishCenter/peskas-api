"""
Column scope definitions.

Scopes define predefined subsets of columns that users can request.
This keeps column name knowledge centralized.

Updated: 2026-01-21 with actual schema from Zanzibar data (18 columns)
"""

# Scope definitions per dataset type
# Format: {dataset_type: {scope_name: [column_list]}}

SCOPE_DEFINITIONS: dict[str, dict[str, list[str]]] = {
    "landings": {
        "core": [
            # Essential columns for basic analysis
            "trip_id",
            "landing_date",
            "gaul_1_code",
            "gaul_1_name",
            "catch_taxon",
            "catch_kg",
        ],
        "detailed": [
            # Extended set with all important fields
            "trip_id",
            "landing_date",
            "gaul_1_code",
            "gaul_1_name",
            "catch_taxon",
            "catch_kg",
            "gear",
            "vessel_type",
            "n_fishers",
            "trip_duration_hrs",
            "catch_price",
            "length_cm",
        ],
        "summary": [
            # Minimal set for quick aggregations
            "landing_date",
            "catch_taxon",
            "catch_kg",
        ],
        "trip": [
            # Trip-level information (without catch details)
            "trip_id",
            "landing_date",
            "gaul_1_code",
            "n_fishers",
            "trip_duration_hrs",
            "gear",
            "vessel_type",
        ],
    },
}


def get_scope_columns(
    scope: str,
    dataset_type: str = "landings",
) -> list[str] | None:
    """
    Get column list for a scope.

    Args:
        scope: Scope name (e.g., 'core', 'detailed')
        dataset_type: Dataset type name

    Returns:
        List of column names, or None if scope not found
    """
    type_scopes = SCOPE_DEFINITIONS.get(dataset_type, {})
    return type_scopes.get(scope)


def get_available_scopes(dataset_type: str = "landings") -> list[str]:
    """Get list of available scope names for a dataset type."""
    return list(SCOPE_DEFINITIONS.get(dataset_type, {}).keys())
