# peskas-api 1.0.0

## New Features

- **Comprehensive Field Metadata**: All 18 data fields now have complete, detailed metadata descriptions:
  - Precise definitions following fishery science terminology
  - Clear explanations of data collection methodology
  - Detailed examples and valid value ranges
  - Units specified for all measurement fields
  - Ontology references for standardized terms (AQFO, FAO ASFIS, GAUL)

- **Dual URL Support for Metadata**: Enhanced metadata schema now distinguishes between:
  - `ontology_url`: Formal ontology definitions (e.g., AQFO terms like `http://w3id.org/aqfo/aqfo_00000022`)
  - `url`: Reference documentation and dataset catalogs (e.g., FAO ASFIS catalog, GAUL dataset pages)
  - Both fields are exposed via metadata endpoints for comprehensive field documentation

## Improvements

- **Enhanced Field Descriptions**:
  - `n_fishers`: Clarified as "total number of people actively fishing on a trip"
  - `trip_duration_hrs`: Added explanation of measurement methodology (between departure and return)
  - `length_cm`: Documented the length class system (ranges for fish <100cm, measured values for fish >1m)
  - `n_catch`: Precise definition of catch record counting (unique taxon × size class combinations)
  - `catch_outcome`: Clarified binary coding (1 = at least one catch, 0 = no catch)
  - Geographic fields: Added clear distinction between GAUL level 1 (States/Provinces) and level 2 (Districts)

- **Ontology Integration**:
  - Added AQFO (Aquaculture and Fisheries Ontology) links for fishing-specific terms
  - FAO ASFIS species list references for taxonomic fields
  - GAUL dataset references for geographic fields
  - Enables semantic web integration and machine-readable definitions

- **API Stability Fixes**:
  - Fixed `AssertionError` in metadata endpoints caused by duplicate `Depends()` declarations
  - Corrected parameter ordering in metadata endpoint functions
  - All metadata endpoints now working correctly and tested

## Bug Fixes

- Fixed metadata endpoint startup crash: Removed redundant `Depends()` from `AuthenticatedUser` parameters
- Fixed Python syntax error: Reordered parameters to place required args before optional ones
- All 22 tests passing successfully

## Documentation

- Updated R integration functions to include new `url` field in metadata responses
- Enhanced `metadata_to_df()` helper function to extract both `ontology_url` and `url` fields

# peskas-api 0.4.0

## New Features

- **Field Metadata Discovery Endpoints**: Added comprehensive metadata endpoints for programmatic field discovery:
  - `GET /api/v1/metadata`: List all available dataset types with metadata
  - `GET /api/v1/metadata/{dataset_type}`: Get detailed metadata for all fields in a dataset type
  - `GET /api/v1/metadata/{dataset_type}/fields/{field_name}`: Get metadata for a specific field
  - Supports optional scope filtering to get metadata for fields in specific scopes
  - Enables applications to dynamically discover available fields, their types, descriptions, units, and possible values

- **Field Metadata Schema**: New centralized field metadata system:
  - Comprehensive field definitions with descriptions, data types, units, and examples
  - Support for value ranges (numeric fields) and possible values (categorical fields)
  - Ontology URL support for semantic web interoperability
  - Machine-readable metadata following FAIR data principles
  - Easy to extend: add new fields by updating `schema/field_metadata.py`

- **FAIR Data Principles Support**: Enhanced metadata follows Findable, Accessible, Interoperable, and Reusable principles:
  - Ontology URL links for fields with formal definitions (e.g., FAO ASFIS, GAUL, Schema.org)
  - Machine-readable field definitions for AI/ML systems
  - Semantic web compatibility for knowledge graph integration
  - Standardized field descriptions and types

## Improvements

- **Enhanced Logging**: Added structured logging to metadata endpoints:
  - INFO logs for successful operations (field retrieval, dataset listing)
  - WARNING logs for validation failures (invalid dataset types, scopes, fields)
  - Consistent logging patterns across all endpoints
  - Improved observability for production monitoring

- **Documentation Enhancements**:
  - Updated README with comprehensive metadata endpoint examples
  - Added metadata discovery examples for Python, R, and JavaScript/TypeScript integrations
  - Enhanced API reference documentation with complete metadata endpoint details
  - Added guidance on using metadata endpoints instead of hardcoding field names
  - Created production readiness review document

- **Code Quality**:
  - Enhanced docstrings with complete `Raises` sections for all endpoints
  - Improved error messages with context and available options
  - Consistent error handling patterns across metadata endpoints
  - All code passes linting checks
  - Production-ready code review completed

- **Response Models**: Added new Pydantic response models:
  - `FieldMetadataResponse`: Metadata for a single field
  - `DatasetMetadataResponse`: Metadata for all fields in a dataset
  - `MetadataListResponse`: List of available dataset types
  - All models include comprehensive field descriptions for automatic OpenAPI documentation

## Documentation

- Updated `README.md` with:
  - Metadata endpoints in endpoints table
  - "Discovering Field Metadata" section with curl examples
  - Enhanced integration examples (Python, R, JavaScript/TypeScript) with metadata discovery functions
  - Updated data schema section with metadata endpoint guidance

- Updated `docs/API_REFERENCE.md` with:
  - Complete metadata endpoints documentation
  - Request/response examples
  - Error response documentation
  - Integration examples

- Created `docs/PRODUCTION_READINESS_REVIEW.md`:
  - Comprehensive production readiness assessment
  - Code quality review
  - Security and performance considerations
  - Deployment readiness checklist

## Technical Details

- **New Modules**:
  - `src/peskas_api/schema/field_metadata.py`: Field metadata definitions and helper functions
  - `src/peskas_api/api/endpoints/metadata.py`: Metadata endpoint implementations

- **Enhanced Modules**:
  - `src/peskas_api/models/responses.py`: Added metadata response models
  - `src/peskas_api/api/router.py`: Added metadata router

- **Metadata Structure**: Each field includes:
  - Name and description
  - Data type (string, integer, float, date, datetime)
  - Unit (kg, cm, hours, etc.)
  - Possible values (for categorical fields)
  - Value ranges (for numeric fields)
  - Examples
  - Ontology URL (optional, for semantic web integration)

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
