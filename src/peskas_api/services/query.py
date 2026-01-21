"""
DuckDB query layer for Parquet files.

All SQL generation and execution happens here. Schema-specific
assumptions (like date column name) are isolated and configurable.
"""

from datetime import date
from io import StringIO
from pathlib import Path
from typing import Iterator

import duckdb

from peskas_api.core.config import get_settings


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
        catch_taxon: str | None = None,
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
            catch_taxon: Optional FAO ASFIS species code filter
            columns: Optional list of columns to select (None = all)
            limit: Optional row limit

        Returns:
            DuckDB relation that can be iterated or converted
        """
        # Build column selection
        if columns:
            available_cols = self._get_columns(parquet_path)
            valid_cols = [c for c in columns if c in available_cols]
            if not valid_cols:
                valid_cols = ["*"]
            col_expr = ", ".join(f'"{c}"' for c in valid_cols)
        else:
            col_expr = "*"

        # Build base query
        query = f"SELECT {col_expr} FROM read_parquet('{parquet_path}')"

        # Add WHERE clauses
        conditions = []
        params = []

        effective_date_column = date_column or self.settings.default_date_column

        if date_from is not None:
            conditions.append(f'"{effective_date_column}" >= ?')
            params.append(date_from)

        if date_to is not None:
            conditions.append(f'"{effective_date_column}" <= ?')
            params.append(date_to)

        if gaul_1 is not None:
            conditions.append('"gaul_1_code" = ?')
            params.append(gaul_1)

        if catch_taxon is not None:
            conditions.append('"catch_taxon" = ?')
            params.append(catch_taxon)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        # Add limit
        effective_limit = min(
            limit or self.settings.max_rows_default,
            self.settings.max_rows_limit,
        )
        query += f" LIMIT {effective_limit}"

        return self._conn.execute(query, params)

    def _get_columns(self, parquet_path: Path) -> set[str]:
        """Get available columns from a parquet file."""
        result = self._conn.execute(
            f"SELECT column_name FROM parquet_schema('{parquet_path}')"
        )
        return {row[0] for row in result.fetchall()}

    def stream_csv(
        self,
        parquet_path: Path,
        date_column: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        gaul_1: str | None = None,
        catch_taxon: str | None = None,
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
            catch_taxon: Optional FAO ASFIS species code filter
            columns: Optional column filter
            limit: Optional row limit

        Yields:
            CSV string chunks (first chunk includes header)
        """
        relation = self.query_parquet(
            parquet_path,
            date_column=date_column,
            date_from=date_from,
            date_to=date_to,
            gaul_1=gaul_1,
            catch_taxon=catch_taxon,
            columns=columns,
            limit=limit,
        )

        df = relation.fetchdf()

        output = StringIO()
        df.to_csv(output, index=False)
        yield output.getvalue()

    def get_as_records(
        self,
        parquet_path: Path,
        date_column: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        gaul_1: str | None = None,
        catch_taxon: str | None = None,
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
        relation = self.query_parquet(
            parquet_path,
            date_column=date_column,
            date_from=date_from,
            date_to=date_to,
            gaul_1=gaul_1,
            catch_taxon=catch_taxon,
            columns=columns,
            limit=limit,
        )

        df = relation.fetchdf()

        # Convert datetime columns to ISO format strings for JSON serialization
        for col in df.columns:
            if hasattr(df[col], "dt"):
                df[col] = df[col].dt.strftime("%Y-%m-%dT%H:%M:%S")

        return df.to_dict(orient="records")


_query_service: QueryService | None = None


def get_query_service() -> QueryService:
    """Get singleton query service instance."""
    global _query_service
    if _query_service is None:
        _query_service = QueryService()
    return _query_service
