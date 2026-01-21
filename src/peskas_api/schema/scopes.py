"""
Column scope definitions.

Scopes define predefined subsets of columns that users can request.
This keeps column name knowledge centralized.

To add or modify scopes, update the SCOPE_DEFINITIONS dictionary below.
Each dataset type can have its own set of scopes.
"""

# Scope definitions per dataset type
# Format: {dataset_type: {scope_name: [column_list]}}
# 
# To add a new scope, add it to the appropriate dataset type dictionary.
# Example:
#   "landings": {
#       "trip_info": [...],
#       "catch_info": [...],
#       "my_new_scope": ["column1", "column2", ...],
#   }

SCOPE_DEFINITIONS: dict[str, dict[str, list[str]]] = {
    "landings": {
        "trip_info": [
            # Trip-level information
            "survey_id",
            "trip_id",
            "landing_date",
            "gaul_1_code",
            "gaul_1_name",
            "gaul_2_code",
            "gaul_2_name",
            "n_fishers",
            "trip_duration_hrs",
            "gear",
            "vessel_type",
            "catch_habitat",
            "catch_outcome",
        ],
        "catch_info": [
            # Catch-level information
            "survey_id",
            "trip_id",
            "catch_taxon",
            "length_cm",
            "catch_kg",
            "catch_price",
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
