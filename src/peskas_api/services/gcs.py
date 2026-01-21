"""
Google Cloud Storage access layer.

Handles path resolution and file downloading. All GCS interactions
are isolated here so storage changes don't ripple through the codebase.

Updated: 2026-01-21 to support versioned parquet files with timestamps
"""

import re
from pathlib import Path

from google.cloud import storage
from google.cloud.exceptions import NotFound

from peskas_api.core.config import get_settings
from peskas_api.core.exceptions import DataNotFoundError
from peskas_api.models.enums import DatasetStatus


class GCSService:
    """Service for accessing Parquet files in GCS."""

    def __init__(self):
        settings = get_settings()
        self.bucket_name = settings.gcs_bucket_name
        self.path_template = settings.gcs_path_template
        self.temp_dir = Path(settings.temp_dir)
        self.temp_dir.mkdir(parents=True, exist_ok=True)

        self._client: storage.Client | None = None

    @property
    def client(self) -> storage.Client:
        """Lazy-load GCS client."""
        if self._client is None:
            settings = get_settings()
            self._client = storage.Client(project=settings.gcs_project_id)
        return self._client

    @property
    def bucket(self) -> storage.Bucket:
        """Get bucket reference."""
        return self.client.bucket(self.bucket_name)

    def _parse_timestamp_from_filename(self, filename: str) -> int | None:
        """
        Extract timestamp from versioned filename.

        Pattern: trips-{status}__{YYYYMMDDHHMMSS}_{hash}__.parquet
        Example: trips-raw__20260120143613_7c6156d__.parquet

        Args:
            filename: Name of the parquet file

        Returns:
            Timestamp as integer (YYYYMMDDHHMMSS format), or None if pattern doesn't match
        """
        settings = get_settings()
        match = re.match(settings.gcs_filename_pattern, filename)
        return int(match.group(1)) if match else None

    def _get_latest_file(self, prefix: str, status: DatasetStatus) -> str:
        """
        Find latest versioned file in GCS folder.

        Args:
            prefix: GCS folder path (e.g., "zanzibar/raw/")
            status: DatasetStatus enum

        Returns:
            Full GCS path of latest version

        Raises:
            DataNotFoundError: If no files found matching pattern
        """
        blobs = self.bucket.list_blobs(prefix=prefix)

        # Filter by pattern and parse timestamps
        versioned_files = []
        for blob in blobs:
            filename = blob.name.split("/")[-1]
            timestamp = self._parse_timestamp_from_filename(filename)
            if timestamp:
                versioned_files.append((timestamp, filename, blob.name))

        if not versioned_files:
            raise DataNotFoundError(
                f"No data files found in gs://{self.bucket_name}/{prefix}"
            )

        # Sort by timestamp (descending) and return latest
        versioned_files.sort(reverse=True)
        latest_timestamp, latest_filename, latest_path = versioned_files[0]

        return latest_path

    def build_object_path(
        self,
        country: str,
        status: DatasetStatus,
    ) -> str:
        """
        Build GCS folder path from parameters.

        Pattern: {country}/{status}/

        Args:
            country: Country identifier (e.g., "zanzibar")
            status: raw or validated

        Returns:
            GCS folder path string
        """
        return self.path_template.format(
            country=country.lower(),
            status=status.value,
        )

    def download_parquet(
        self,
        country: str,
        status: DatasetStatus,
    ) -> Path:
        """
        Download the latest versioned Parquet file from GCS to local temp storage.

        Args:
            country: Country identifier (e.g., "zanzibar")
            status: raw or validated

        Returns:
            Path to local parquet file

        Raises:
            DataNotFoundError: If no files exist in GCS folder
        """
        folder_path = self.build_object_path(country, status)

        # Find latest versioned file
        try:
            latest_file_path = self._get_latest_file(folder_path, status)
        except DataNotFoundError:
            raise DataNotFoundError(
                f"No data found for {country}/{status.value}"
            )

        blob = self.bucket.blob(latest_file_path)

        # Extract filename and timestamp for cache key
        filename = latest_file_path.split("/")[-1]
        timestamp = self._parse_timestamp_from_filename(filename)

        # Create deterministic local path for caching (include version)
        cache_key = f"{country}_{status.value}_{timestamp}"
        local_path = self.temp_dir / f"{cache_key}.parquet"

        # Download if not already cached
        if not local_path.exists():
            try:
                blob.download_to_filename(str(local_path))
            except NotFound:
                raise DataNotFoundError(
                    f"No data found for {country}/{status.value}"
                )

        return local_path

    def list_available_countries(self) -> list[str]:
        """
        List available countries in the GCS bucket.

        Useful for metadata endpoint and validation.

        Returns:
            List of country identifiers (lowercase)
        """
        blobs = self.bucket.list_blobs(delimiter="/")

        countries = []
        for prefix in blobs.prefixes:
            # Remove trailing slash and add to list
            country = prefix.rstrip("/")
            if country:
                countries.append(country)

        return sorted(countries)


_gcs_service: GCSService | None = None


def get_gcs_service() -> GCSService:
    """Get singleton GCS service instance."""
    global _gcs_service
    if _gcs_service is None:
        _gcs_service = GCSService()
    return _gcs_service
