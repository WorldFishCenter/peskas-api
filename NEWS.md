# peskas-api 0.3.0

## New Features

- **Additional Filter Parameters**: Added two new optional query parameters for more granular data filtering:
  - `gaul_2`: Filter by GAUL level 2 administrative code (e.g., `16961`)
  - `survey_id`: Filter by survey identifier (e.g., `survey_001`)
  - Both parameters follow the same pattern as existing filters: optional, empty means "return all"

## Improvements

- **Complete Documentation Overhaul**: Updated all documentation to accurately reflect the current API implementation:
  - Removed incorrect references to non-existent `year` parameter
  - Updated all code examples across documentation files
  - Corrected GCS path patterns to show versioned filename structure
  - Updated country identifier examples to use actual values (`zanzibar`, `timor` instead of `TLS`, `IDN`)
  - Clarified that only `/data/landings` endpoint exists (trip data is included in landings dataset)
  - Fixed scope documentation to reflect actual scopes (`trip_info`, `catch_info`)
  
- **Enhanced Integration Guide**: Added comprehensive integration examples in README:
  - Python integration with pandas and requests
  - R integration with httr package
  - JavaScript/TypeScript client implementation
  - Error handling best practices
  - Response format examples
  - Performance optimization tips
  - Rate limiting recommendations

- **API Consistency**: All filter parameters now follow consistent behavior:
  - Empty/null values mean "return all data" for that filter dimension
  - Single value only (consistent across all filters)
  - Multiple filters combine with AND logic
  - Documented in README and API reference

- **Enhanced Health Check**: Health check endpoint now includes:
  - GCS bucket connectivity test
  - Status field: "healthy" or "degraded"
  - `gcs_accessible` boolean field
  - Helpful for monitoring and alerting

- **Production Readiness**:
  - Fixed all failing tests (100% test pass rate)
  - Updated FastAPI interactive docs (/docs) with correct parameter descriptions
  - All code passes linting checks
  - Comprehensive production readiness review completed

## Bug Fixes

- Fixed `test_scope_parsing` test to use correct scope name (`trip_info` instead of `core`)
- Updated health check test to handle GCS unavailability in test environments

## Documentation

- Updated files: `README.md`, `docs/API_REFERENCE.md`, `docs/README.md`, `docs/DEVELOPER_GUIDE.md`, `docs/SETUP_GUIDE.md`
- Added comprehensive API integration section with code examples
- Clarified filter behavior and usage patterns
- All examples now use correct parameter names and values
- Added `PRODUCTION_READINESS_PLAN.md` with comprehensive review



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
