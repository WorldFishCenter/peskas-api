# peskas-api 0.2.0

## Breaking Changes

- **Updated Scope Definitions**: Replaced previous scope options (`core`, `detailed`, `summary`, `trip`) with two focused scopes:
  - `trip_info`: Trip-level information (13 columns including survey_id, trip_id, landing_date, location, gear, vessel details)
  - `catch_info`: Catch-level information (6 columns including survey_id, trip_id, catch_taxon, length, weight, price)

## Improvements

- **Production Readiness**: Comprehensive improvements for production deployment
  - Replaced all `print()` statements with structured logging using Python's `logging` module
  - Added request/response logging middleware with processing time tracking
  - Enhanced error handling with request context and better error messages
  - Improved input validation for all parameters with clear error messages

- **Security Enhancements**:
  - Added SQL injection protection through column name validation and sanitization
  - File path SQL escaping for additional safety
  - Date column name validation before use in queries

- **Error Handling**:
  - Comprehensive exception handling with proper HTTP status codes
  - Edge case handling: empty results, missing files, invalid inputs, timestamp parsing failures
  - Scope validation with helpful error messages listing available options
  - Temp directory writability validation at startup

- **Code Quality**:
  - Version management now reads from package metadata instead of hardcoded values
  - Improved code consistency and maintainability
  - Enhanced documentation and updated API examples

# peskas-api 0.1.0

## New Features

- **Multi-country Fishery Data API**: FastAPI-based REST API for accessing small-scale fishery data
  - Serves data from versioned Parquet files stored in Google Cloud Storage
  - Uses DuckDB for efficient querying of Parquet files on demand
  - Supports both CSV and JSON response formats

- **Dataset Endpoints**:
  - `/api/v1/data/landings`: Retrieve fish landing records with catch and trip information
  - Dynamic endpoint creation based on dataset configuration

- **Query Parameters**:
  - `country`: Filter by country identifier (required)
  - `status`: Choose between `raw` or `validated` datasets (default: `validated`)
  - `date_from` / `date_to`: Filter by date range (YYYY-MM-DD format)
  - `gaul_1`: Filter by GAUL level 1 administrative code
  - `catch_taxon`: Filter by FAO ASFIS species code
  - `scope`: Predefined column sets (`trip_info`, `catch_info`)
  - `limit`: Maximum number of rows to return (1-1,000,000)
  - `format`: Response format (`csv` or `json`, default: `csv`)

- **Scope Definitions**:
  - `trip_info`: Trip-level information (13 columns: survey_id, trip_id, landing_date, location, gear, vessel details)
  - `catch_info`: Catch-level information (6 columns: survey_id, trip_id, catch_taxon, length, weight, price)

- **Authentication**: API key authentication via `X-API-Key` header

- **Health Check**: `/api/v1/health` endpoint for service status monitoring

## Infrastructure

- **Deployment**: Deployed to Google Cloud Run with automatic scaling
- **Containerization**: Multi-stage Docker build for optimized production images
- **CI/CD**: GitHub Actions workflows for automated deployment and releases
- **Documentation**: Comprehensive API reference and deployment guides

## Improvements

- **Performance**: Efficient Parquet file caching and DuckDB querying
- **Error Handling**: Comprehensive error responses with clear messages
- **Security**: Non-root container user, minimal permissions service account
