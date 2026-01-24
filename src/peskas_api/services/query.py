"""
DuckDB query layer for Parquet files.

All SQL generation and execution happens here. Schema-specific
assumptions (like date column name) are isolated and configurable.
"""

import logging
import math
import re
from datetime import date
from io import StringIO
from pathlib import Path
from typing import Iterator

import duckdb
import pandas as pd

from peskas_api.core.config import get_settings

logger = logging.getLogger(__name__)


class QueryService:
    """Service for querying Parquet files with DuckDB."""

    def __init__(self):
        self.settings = get_settings()
        self._conn = duckdb.connect(":memory:")

    def query_parquet(
        self,
        parquet_path: Path,
        date_column: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        gaul_1: str | None = None,
        gaul_2: str | None = None,
        catch_taxon: str | None = None,
        survey_id: str | None = None,
        columns: list[str] | None = None,
        limit: int | None = None,
    ) -> duckdb.DuckDBPyRelation:
        """
        Query a Parquet file with optional filtering.

        Args:
            parquet_path: Path to local parquet file
            date_column: Column to use for date filtering (uses config default if None)
            date_from: Optional start date filter (inclusive)
            date_to: Optional end date filter (inclusive)
            gaul_1: Optional GAUL level 1 code filter
            gaul_2: Optional GAUL level 2 code filter
            catch_taxon: Optional FAO ASFIS species code filter
            survey_id: Optional survey identifier filter
            columns: Optional list of columns to select (None = all)
            limit: Optional row limit

        Returns:
            DuckDB relation that can be iterated or converted
        """
        # Build column selection with validation
        if columns:
            available_cols = self._get_columns(parquet_path)
            valid_cols = self._sanitize_columns(columns, available_cols)
            if not valid_cols:
                logger.warning("No valid columns after sanitization, using all columns")
                col_expr = "*"
            else:
                # Double-quote column names to handle special characters safely
                col_expr = ", ".join(f'"{c}"' for c in valid_cols)
        else:
            col_expr = "*"

        # Validate parquet file exists
        if not parquet_path.exists():
            raise FileNotFoundError(f"Parquet file not found: {parquet_path}")
        
        # Build base query - escape single quotes in path for SQL safety
        escaped_path = str(parquet_path).replace("'", "''")
        query = f"SELECT {col_expr} FROM read_parquet('{escaped_path}')"

        # Add WHERE clauses
        conditions = []
        params = []

        effective_date_column = date_column or self.settings.default_date_column
        
        # Validate date column name is safe
        if not self._validate_column_name(effective_date_column):
            raise ValueError(f"Invalid date column name: {effective_date_column}")

        if date_from is not None:
            conditions.append(f'"{effective_date_column}" >= ?')
            params.append(date_from)

        if date_to is not None:
            conditions.append(f'"{effective_date_column}" <= ?')
            params.append(date_to)

        if gaul_1 is not None:
            conditions.append('"gaul_1_code" = ?')
            params.append(gaul_1)

        if gaul_2 is not None:
            conditions.append('"gaul_2_code" = ?')
            params.append(gaul_2)

        if catch_taxon is not None:
            conditions.append('"catch_taxon" = ?')
            params.append(catch_taxon)

        if survey_id is not None:
            conditions.append('"survey_id" = ?')
            params.append(survey_id)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        # Add limit with validation
        if limit is not None and limit < 1:
            raise ValueError(f"Limit must be >= 1, got {limit}")
        
        effective_limit = min(
            limit or self.settings.max_rows_default,
            self.settings.max_rows_limit,
        )
        query += f" LIMIT {effective_limit}"

        try:
            return self._conn.execute(query, params)
        except Exception as e:
            logger.error(f"DuckDB query execution failed: {e} - Query: {query[:200]}")
            raise ValueError(f"Query execution failed: {e}") from e

    def _validate_column_name(self, column: str) -> bool:
        """
        Validate that a column name is safe for use in SQL.
        
        Only allows alphanumeric characters, underscores, and hyphens.
        Prevents SQL injection through column names.
        """
        # Safe pattern: alphanumeric, underscore, hyphen
        return bool(re.match(r'^[a-zA-Z0-9_-]+$', column))
    
    def _get_columns(self, parquet_path: Path) -> set[str]:
        """Get available columns from a parquet file."""
        try:
            escaped_path = str(parquet_path).replace("'", "''")
            # Read a single row to get column names from the DataFrame
            # This is more reliable than trying to parse parquet_schema()
            result = self._conn.execute(
                f"SELECT * FROM read_parquet('{escaped_path}') LIMIT 1"
            )
            df = result.fetchdf()
            return set(df.columns)
        except Exception as e:
            logger.error(f"Failed to read parquet schema from {parquet_path}: {e}")
            raise ValueError(f"Cannot read parquet file schema: {parquet_path}") from e
    
    def _sanitize_columns(self, columns: list[str], available: set[str]) -> list[str]:
        """
        Sanitize and validate column names against available columns.
        
        Filters out invalid or non-existent columns and logs warnings.
        """
        valid_cols = []
        for col in columns:
            if not self._validate_column_name(col):
                logger.warning(f"Invalid column name rejected: {col}")
                continue
            if col not in available:
                logger.warning(f"Column not found in schema: {col}")
                continue
            valid_cols.append(col)
        return valid_cols

    def stream_csv(
        self,
        parquet_path: Path,
        date_column: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        gaul_1: str | None = None,
        gaul_2: str | None = None,
        catch_taxon: str | None = None,
        survey_id: str | None = None,
        columns: list[str] | None = None,
        limit: int | None = None,
    ) -> Iterator[str]:
        """
        Stream query results as CSV chunks.

        This enables efficient streaming of large datasets without
        loading everything into memory.

        Args:
            parquet_path: Path to parquet file
            date_column: Column for date filtering
            date_from: Optional start date
            date_to: Optional end date
            gaul_1: Optional GAUL level 1 code filter
            gaul_2: Optional GAUL level 2 code filter
            catch_taxon: Optional FAO ASFIS species code filter
            survey_id: Optional survey identifier filter
            columns: Optional column filter
            limit: Optional row limit

        Yields:
            CSV string chunks (first chunk includes header)
        """
        try:
            relation = self.query_parquet(
                parquet_path,
                date_column=date_column,
                date_from=date_from,
                date_to=date_to,
                gaul_1=gaul_1,
                gaul_2=gaul_2,
                catch_taxon=catch_taxon,
                survey_id=survey_id,
                columns=columns,
                limit=limit,
            )

            df = relation.fetchdf()
            
            # Handle empty results
            if df.empty:
                logger.info("Query returned empty result set")
                # Return CSV with headers only if columns were specified
                if columns:
                    output = StringIO()
                    pd.DataFrame(columns=columns).to_csv(output, index=False)
                    yield output.getvalue()
                else:
                    yield ""
                return

            output = StringIO()
            df.to_csv(output, index=False)
            yield output.getvalue()
        except Exception as e:
            logger.error(f"Error during CSV streaming: {e}", exc_info=True)
            raise

    def get_as_records(
        self,
        parquet_path: Path,
        date_column: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        gaul_1: str | None = None,
        gaul_2: str | None = None,
        catch_taxon: str | None = None,
        survey_id: str | None = None,
        columns: list[str] | None = None,
        limit: int | None = None,
    ) -> list[dict]:
        """
        Get query results as list of dictionaries (for JSON response).

        Args:
            Same as query_parquet

        Returns:
            List of row dictionaries with JSON-serializable values
        """
        try:
            relation = self.query_parquet(
                parquet_path,
                date_column=date_column,
                date_from=date_from,
                date_to=date_to,
                gaul_1=gaul_1,
                gaul_2=gaul_2,
                catch_taxon=catch_taxon,
                survey_id=survey_id,
                columns=columns,
                limit=limit,
            )

            df = relation.fetchdf()
            
            # Handle empty results
            if df.empty:
                logger.info("Query returned empty result set")
                return []

            # Convert datetime columns to ISO format strings for JSON serialization
            for col in df.columns:
                if hasattr(df[col], "dt"):
                    df[col] = df[col].dt.strftime("%Y-%m-%dT%H:%M:%S")
            
            # Replace NaN, Infinity, -Infinity with None for JSON serialization
            df = df.replace([float('nan'), float('inf'), float('-inf')], None)
            
            # Convert to dict and handle remaining NaN values
            records = df.to_dict(orient="records")
            
            # Additional pass to ensure no NaN values remain (safety check)
            for record in records:
                for key, value in record.items():
                    if isinstance(value, float):
                        if math.isnan(value) or math.isinf(value):
                            record[key] = None
            
            return records
        except Exception as e:
            logger.error(f"Error during record retrieval: {e}", exc_info=True)
            raise


_query_service: QueryService | None = None


def get_query_service() -> QueryService:
    """Get singleton query service instance."""
    global _query_service
    if _query_service is None:
        _query_service = QueryService()
    return _query_service
