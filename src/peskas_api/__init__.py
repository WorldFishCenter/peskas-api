"""Peskas Multi-country Fishery Data API."""

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("peskas-api")
except PackageNotFoundError:
    # Fallback for development when package is not installed
    __version__ = "0.1.0"
