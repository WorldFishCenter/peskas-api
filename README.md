# Peskas Multi-country Fishery Data API

A FastAPI service that exposes validated multi-country small-scale fishery data from Parquet files stored in Google Cloud Storage (GCS), using DuckDB as the query engine.

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [API Usage](#api-usage)
- [Configuration](#configuration)
- [Development](#development)
- [Deployment](#deployment)

## Overview

**Stack**: FastAPI + DuckDB + GCS + Parquet → Cloud Run

This API provides:
- Access to fishery data from multiple countries
- Filtering by country and dataset status (raw/validated)
- Date range filtering within datasets
- GAUL administrative code filtering (levels 1 and 2)
- FAO ASFIS species code filtering
- Survey identifier filtering
- Column selection via predefined scopes (trip_info or catch_info)
- CSV streaming (default) and JSON output
- **Field metadata discovery** - Programmatically discover available fields, their types, descriptions, units, and ontology links

**Key Design Principles**:
- **Schema flexibility**: Column names and dataset types are configurable and can evolve
- **Low cost**: Serverless Cloud Run + GCS storage, no database overhead
- **Maintainable**: Clear module separation, well-documented code
- **Extensible**: Add new dataset types by updating a single config file

## Quick Start

### Prerequisites

- Python 3.11+
- Google Cloud credentials (for GCS access)
- GCS bucket with Parquet files

### Local Development

```bash
# Clone repository
cd peskas-api

# Create virtual environment with Python 3.11+
python3.11 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e ".[dev]"

# Set up environment variables
cp .env.example .env
# Edit .env with your settings

# Run tests
pytest -v

# Start development server
uvicorn peskas_api.main:app --reload --port 8000
```

Visit:
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/api/v1/health

## Project Structure

```
peskas-api/
├── src/peskas_api/
│   ├── main.py                  # FastAPI app entry point
│   │
│   ├── api/                     # API routes and endpoints
│   │   ├── router.py            # Main router aggregator
│   │   ├── deps.py              # Shared dependencies (auth, services)
│   │   └── endpoints/
│   │       ├── health.py        # Health check (no auth)
│   │       └── datasets.py      # Data endpoints (dynamic)
│   │
│   ├── core/                    # Configuration and utilities
│   │   ├── config.py            # Settings from environment
│   │   ├── auth.py              # API key authentication
│   │   └── exceptions.py        # Custom exceptions + handlers
│   │
│   ├── models/                  # Pydantic schemas
│   │   ├── enums.py             # DatasetStatus, ResponseFormat
│   │   ├── params.py            # Query parameter schemas
│   │   └── responses.py         # Response schemas
│   │
│   ├── services/                # Business logic
│   │   ├── gcs.py               # GCS path building + download
│   │   └── query.py             # DuckDB querying + CSV streaming
│   │
│   └── schema/                  # Data schema configuration
│       ├── dataset_config.py    # Dataset type registry
│       └── scopes.py            # Column scope mappings
│
├── tests/                       # Test suite
├── Dockerfile                   # Container build
├── pyproject.toml               # Dependencies
└── .env.example                 # Environment template
```

### Key Modules

- **core/config.py**: All settings loaded from environment variables
- **schema/dataset_config.py**: Registry of dataset types - add new types here
- **schema/scopes.py**: Column name mappings - update when schema changes
- **services/gcs.py**: GCS file path resolution and downloading
- **services/query.py**: DuckDB query execution with date filtering

## API Usage

### Authentication

All data endpoints require an API key in the `X-API-Key` header:

```bash
curl -H "X-API-Key: your-secret-key" \
  "http://localhost:8000/api/v1/data/landings?country=zanzibar"
```

### Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/v1/health` | No | Health check |
| GET | `/api/v1/data/landings` | Yes | Fish landing records with trip information |
| GET | `/api/v1/metadata` | Yes | List available dataset types with metadata |
| GET | `/api/v1/metadata/{dataset_type}` | Yes | Get field metadata for a dataset type |
| GET | `/api/v1/metadata/{dataset_type}/fields/{field_name}` | Yes | Get metadata for a specific field |

### Query Parameters

**Required**:
- `country`: Country identifier (e.g., `zanzibar`, `timor`)

**Optional**:
- `status`: `raw` or `validated` (default: `validated`)
- `date_from`: Start date `YYYY-MM-DD` (inclusive)
- `date_to`: End date `YYYY-MM-DD` (inclusive)
- `gaul_1`: GAUL level 1 administrative code filter (e.g., `1696`)
- `gaul_2`: GAUL level 2 administrative code filter (e.g., `16961`)
- `catch_taxon`: FAO ASFIS species code filter (e.g., `MZZ`, `SKJ`)
- `survey_id`: Survey identifier filter (e.g., `survey_001`)
- `scope`: Predefined column set (`trip_info` or `catch_info`)
- `limit`: Max rows to return (default: 100,000, max: 1,000,000)
- `format`: `csv` (default) or `json`

**Filter Behavior**:
- All filters are optional - if not specified, returns all matching data
- Multiple filters can be combined (AND logic)
- Empty/null values mean "return all" for that dimension

### Examples

**Get validated landings data for Zanzibar (CSV)**:
```bash
curl -H "X-API-Key: your-key" \
  "http://localhost:8000/api/v1/data/landings?country=zanzibar"
```

**Get raw data with date filtering (JSON)**:
```bash
curl -H "X-API-Key: your-key" \
  "http://localhost:8000/api/v1/data/landings?country=zanzibar&status=raw&date_from=2025-02-01&date_to=2025-02-28&format=json"
```

**Filter by GAUL administrative code**:
```bash
curl -H "X-API-Key: your-key" \
  "http://localhost:8000/api/v1/data/landings?country=zanzibar&gaul_1=1696&format=json"
```

**Filter by species (FAO ASFIS code)**:
```bash
curl -H "X-API-Key: your-key" \
  "http://localhost:8000/api/v1/data/landings?country=zanzibar&catch_taxon=MZZ&format=json"
```

**Get trip-level information only**:
```bash
curl -H "X-API-Key: your-key" \
  "http://localhost:8000/api/v1/data/landings?country=zanzibar&scope=trip_info"
```

**Get catch-level information only**:
```bash
curl -H "X-API-Key: your-key" \
  "http://localhost:8000/api/v1/data/landings?country=zanzibar&scope=catch_info"
```

**Combined filters**:
```bash
curl -H "X-API-Key: your-key" \
  "http://localhost:8000/api/v1/data/landings?country=zanzibar&gaul_1=1696&gaul_2=16961&catch_taxon=SKJ&survey_id=survey_001&date_from=2025-02-01&scope=trip_info&format=json"
```

### Discovering Field Metadata

Before querying data, you can discover what fields are available and what they mean:

**List available dataset types**:
```bash
curl -H "X-API-Key: your-key" \
  "http://localhost:8000/api/v1/metadata"
```

**Get all field metadata for a dataset**:
```bash
curl -H "X-API-Key: your-key" \
  "http://localhost:8000/api/v1/metadata/landings"
```

**Get metadata for fields in a specific scope**:
```bash
curl -H "X-API-Key: your-key" \
  "http://localhost:8000/api/v1/metadata/landings?scope=trip_info"
```

**Get metadata for a single field**:
```bash
curl -H "X-API-Key: your-key" \
  "http://localhost:8000/api/v1/metadata/landings/fields/catch_kg"
```

The metadata response includes:
- Field descriptions
- Data types (string, integer, float, datetime)
- Units (kg, cm, hours, etc.)
- Possible values (for categorical fields)
- Value ranges (for numeric fields)
- Examples
- Ontology URLs (for semantic web interoperability)

---

## Integration Guide

### Python Integration

```python
import requests
import pandas as pd
from io import StringIO

API_URL = "http://localhost:8000/api/v1"
API_KEY = "your-api-key"

# Get data as CSV and load into pandas
def get_landings_csv(country, **filters):
    """Fetch landings data as pandas DataFrame."""
    params = {"country": country, **filters}
    
    response = requests.get(
        f"{API_URL}/data/landings",
        params=params,
        headers={"X-API-Key": API_KEY}
    )
    response.raise_for_status()
    
    return pd.read_csv(StringIO(response.text))

# Get data as JSON
def get_landings_json(country, **filters):
    """Fetch landings data as list of dictionaries."""
    params = {"country": country, "format": "json", **filters}
    
    response = requests.get(
        f"{API_URL}/data/landings",
        params=params,
        headers={"X-API-Key": API_KEY}
    )
    response.raise_for_status()
    
    return response.json()["data"]

# Discover field metadata
def get_field_metadata(dataset_type="landings", field_name=None, scope=None):
    """Get metadata for fields in a dataset."""
    if field_name:
        url = f"{API_URL}/metadata/{dataset_type}/fields/{field_name}"
    else:
        url = f"{API_URL}/metadata/{dataset_type}"
        if scope:
            url += f"?scope={scope}"
    
    response = requests.get(
        url,
        headers={"X-API-Key": API_KEY}
    )
    response.raise_for_status()
    return response.json()

# Example: Discover available fields
metadata = get_field_metadata("landings")
print("Available fields:")
for field_name, field_info in metadata["fields"].items():
    print(f"  {field_name}: {field_info['description']}")
    if field_info.get("unit"):
        print(f"    Unit: {field_info['unit']}")
    if field_info.get("possible_values"):
        print(f"    Possible values: {', '.join(field_info['possible_values'][:5])}")

# Example: Get metadata for a specific field
catch_kg_metadata = get_field_metadata("landings", field_name="catch_kg")
print(f"\ncatch_kg metadata:")
print(f"  Description: {catch_kg_metadata['description']}")
print(f"  Unit: {catch_kg_metadata['unit']}")
print(f"  Value range: {catch_kg_metadata['value_range']}")

# Example usage: Fetch data
df = get_landings_csv(
    country="zanzibar",
    date_from="2023-01-01",
    date_to="2023-12-31",
    gaul_1="1696",
    scope="trip_info"
)

print(f"\nFetched {len(df)} records")
print(df.head())
```

### R Integration

```r
library(httr)
library(jsonlite)

API_URL <- "http://localhost:8000/api/v1"
API_KEY <- "your-api-key"

#' Get landings data from Peskas API
#' 
#' @param country Country identifier (required)
#' @param ... Additional query parameters (date_from, date_to, gaul_1, etc.)
#' @return Data frame with landings data
get_landings_data <- function(country, ...) {
  params <- list(country = country, ...)
  
  response <- GET(
    paste0(API_URL, "/data/landings"),
    query = params,
    add_headers("X-API-Key" = API_KEY)
  )
  
  stop_for_status(response)
  
  # Parse CSV response
  content <- content(response, "text", encoding = "UTF-8")
  df <- read.csv(text = content, stringsAsFactors = FALSE)
  
  return(df)
}

#' Get field metadata from Peskas API
#' 
#' @param dataset_type Dataset type (default: "landings")
#' @param field_name Optional field name for single field metadata
#' @param scope Optional scope name to filter fields
#' @return List with field metadata
get_field_metadata <- function(dataset_type = "landings", field_name = NULL, scope = NULL) {
  if (!is.null(field_name)) {
    url <- paste0(API_URL, "/metadata/", dataset_type, "/fields/", field_name)
  } else {
    url <- paste0(API_URL, "/metadata/", dataset_type)
    if (!is.null(scope)) {
      url <- paste0(url, "?scope=", scope)
    }
  }
  
  response <- GET(
    url,
    add_headers("X-API-Key" = API_KEY)
  )
  
  stop_for_status(response)
  return(fromJSON(content(response, "text")))
}

# Example: Discover available fields
metadata <- get_field_metadata("landings")
cat("Available fields:\n")
for (field_name in names(metadata$fields)) {
  field_info <- metadata$fields[[field_name]]
  cat(sprintf("  %s: %s\n", field_name, field_info$description))
  if (!is.null(field_info$unit)) {
    cat(sprintf("    Unit: %s\n", field_info$unit))
  }
}

# Example usage: Fetch data
df <- get_landings_data(
  country = "zanzibar",
  date_from = "2023-01-01",
  date_to = "2023-12-31",
  gaul_1 = "1696",
  scope = "trip_info"
)

cat(sprintf("\nFetched %d records\n", nrow(df)))
head(df)
```

### JavaScript/TypeScript Integration

```typescript
interface LandingsParams {
  country: string;
  status?: 'raw' | 'validated';
  date_from?: string;
  date_to?: string;
  gaul_1?: string;
  gaul_2?: string;
  catch_taxon?: string;
  survey_id?: string;
  scope?: 'trip_info' | 'catch_info';
  limit?: number;
  format?: 'csv' | 'json';
}

interface LandingsRecord {
  [key: string]: string | number | null;
}

interface FieldMetadata {
  name: string;
  description: string;
  data_type: string;
  unit: string | null;
  possible_values: string[] | null;
  value_range: [number | null, number | null] | null;
  examples: any[] | null;
  required: boolean;
  ontology_url: string | null;
}

interface DatasetMetadata {
  dataset_type: string;
  fields: Record<string, FieldMetadata>;
}

class PeskasAPIClient {
  constructor(
    private apiUrl: string,
    private apiKey: string
  ) {}

  async getLandings(params: LandingsParams): Promise<LandingsRecord[]> {
    const queryParams = new URLSearchParams(
      Object.entries({ ...params, format: 'json' })
        .filter(([_, v]) => v !== undefined)
        .map(([k, v]) => [k, String(v)])
    );

    const response = await fetch(
      `${this.apiUrl}/data/landings?${queryParams}`,
      {
        headers: {
          'X-API-Key': this.apiKey
        }
      }
    );

    if (!response.ok) {
      throw new Error(`API error: ${response.status} ${response.statusText}`);
    }

    const result = await response.json();
    return result.data;
  }

  async getLandingsCSV(params: LandingsParams): Promise<string> {
    const queryParams = new URLSearchParams(
      Object.entries({ ...params, format: 'csv' })
        .filter(([_, v]) => v !== undefined)
        .map(([k, v]) => [k, String(v)])
    );

    const response = await fetch(
      `${this.apiUrl}/data/landings?${queryParams}`,
      {
        headers: {
          'X-API-Key': this.apiKey
        }
      }
    );

    if (!response.ok) {
      throw new Error(`API error: ${response.status} ${response.statusText}`);
    }

    return await response.text();
  }

  async getFieldMetadata(
    datasetType: string = 'landings',
    fieldName?: string,
    scope?: string
  ): Promise<DatasetMetadata | FieldMetadata> {
    let url = `${this.apiUrl}/metadata/${datasetType}`;
    if (fieldName) {
      url = `${this.apiUrl}/metadata/${datasetType}/fields/${fieldName}`;
    } else if (scope) {
      url += `?scope=${scope}`;
    }

    const response = await fetch(url, {
      headers: {
        'X-API-Key': this.apiKey
      }
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status} ${response.statusText}`);
    }

    return await response.json();
  }
}

// Example usage
const client = new PeskasAPIClient(
  'http://localhost:8000/api/v1',
  'your-api-key'
);

// Discover available fields
const metadata = await client.getFieldMetadata('landings') as DatasetMetadata;
console.log('Available fields:');
Object.entries(metadata.fields).forEach(([name, info]) => {
  console.log(`  ${name}: ${info.description}`);
  if (info.unit) console.log(`    Unit: ${info.unit}`);
});

// Fetch data
const data = await client.getLandings({
  country: 'zanzibar',
  date_from: '2023-01-01',
  date_to: '2023-12-31',
  gaul_1: '1696',
  scope: 'trip_info',
  limit: 1000
});

console.log(`\nFetched ${data.length} records`);
```

### Error Handling

All integrations should handle these HTTP status codes:

| Code | Meaning | Action |
|------|---------|--------|
| 200 | Success | Process the response data |
| 400 | Bad Request | Check parameter values and formats |
| 401 | Unauthorized | Verify API key is included in headers |
| 403 | Forbidden | Check API key validity |
| 404 | Not Found | No data exists for the specified filters |
| 422 | Validation Error | Check required parameters and data types |
| 500 | Server Error | Retry with exponential backoff |

**Example error handling (Python)**:

```python
from requests.exceptions import HTTPError
import time

def get_landings_with_retry(country, max_retries=3, **filters):
    """Fetch landings data with retry logic."""
    for attempt in range(max_retries):
        try:
            response = requests.get(
                f"{API_URL}/data/landings",
                params={"country": country, **filters},
                headers={"X-API-Key": API_KEY},
                timeout=30
            )
            response.raise_for_status()
            return pd.read_csv(StringIO(response.text))
            
        except HTTPError as e:
            if e.response.status_code in [400, 401, 403, 404, 422]:
                # Client errors - don't retry
                print(f"Client error: {e.response.json()}")
                raise
            elif e.response.status_code >= 500:
                # Server errors - retry with backoff
                if attempt < max_retries - 1:
                    wait = 2 ** attempt  # Exponential backoff
                    print(f"Server error, retrying in {wait}s...")
                    time.sleep(wait)
                else:
                    raise
        except Exception as e:
            print(f"Unexpected error: {e}")
            raise
```

### Response Formats

**CSV Response** (default):
```csv
trip_id,landing_date,gaul_1_code,gaul_1_name,catch_taxon,catch_kg
trip_001,2023-01-15,1696,Unguja,SKJ,45.2
trip_002,2023-01-16,1696,Unguja,MZZ,32.8
```

**JSON Response** (`format=json`):
```json
{
  "data": [
    {
      "trip_id": "trip_001",
      "landing_date": "2023-01-15T00:00:00",
      "gaul_1_code": "1696",
      "gaul_1_name": "Unguja",
      "catch_taxon": "SKJ",
      "catch_kg": 45.2
    },
    {
      "trip_id": "trip_002",
      "landing_date": "2023-01-16T00:00:00",
      "gaul_1_code": "1696",
      "gaul_1_name": "Unguja",
      "catch_taxon": "MZZ",
      "catch_kg": 32.8
    }
  ]
}
```

### Rate Limiting & Best Practices

**Current Status**: No rate limits enforced

**Recommendations**:
- Use the `limit` parameter to control response size
- Cache responses when appropriate
- Use `date_from`/`date_to` to fetch incremental updates
- Request only needed columns using `scope` parameter
- Use CSV format for large datasets (more efficient than JSON)
- Implement retry logic with exponential backoff for server errors

**Performance Tips**:
- Smaller date ranges = faster responses
- Using `scope` reduces data transfer
- CSV format is ~30% smaller than JSON for large datasets
- `limit` parameter helps with pagination

---

## Configuration

### Environment Variables

Create a `.env` file (see [.env.example](.env.example)):

```bash
# Required
API_SECRET_KEY=your-secure-random-string
GCS_BUCKET_NAME=your-gcs-bucket-name

# Optional
DEBUG=false
GCS_PROJECT_ID=your-gcp-project-id
DEFAULT_DATE_COLUMN=date
DEFAULT_STATUS=validated
MAX_ROWS_DEFAULT=100000
MAX_ROWS_LIMIT=1000000
```

### GCS Data Layout

Parquet files must follow this structure:

```
gs://your-bucket/
  zanzibar/
    raw/
      trips-raw__20260120143613_7c6156d__.parquet
      trips-raw__20260121120000_abc1234__.parquet (newer version)
    validated/
      trips-validated__20260120143613_7c6156d__.parquet
```

Pattern: `{country}/{status}/trips-{status}__{YYYYMMDDHHMMSS}_{hash}__.parquet`

**Versioning**: Multiple versions can exist in the same folder. The API automatically selects the latest file by timestamp.

## Development

### Running Tests

```bash
# Run all tests
pytest -v

# Run specific test file
pytest tests/test_auth.py -v

# Run with coverage
pytest --cov=peskas_api --cov-report=html
```

### Data Schema

The current schema includes 18 columns per record:

**Trip-level columns** (13 columns):
- `survey_id`: Survey identifier
- `trip_id`: Trip identifier
- `landing_date`: Date of landing
- `gaul_1_code`, `gaul_1_name`: GAUL level 1 administrative codes
- `gaul_2_code`, `gaul_2_name`: GAUL level 2 administrative codes
- `n_fishers`: Number of fishers
- `trip_duration_hrs`: Trip duration in hours
- `gear`: Fishing gear type
- `vessel_type`: Type of vessel
- `catch_habitat`: Habitat code
- `catch_outcome`: Outcome code

**Catch-level columns** (6 columns):
- `survey_id`: Survey identifier (linking field)
- `trip_id`: Trip identifier (linking field)
- `catch_taxon`: FAO ASFIS species code
- `length_cm`: Fish length in centimeters
- `catch_kg`: Catch weight in kilograms
- `catch_price`: Price in local currency

**Note**: `n_catch` column mentioned in earlier documentation is not currently in the defined scopes.

**Predefined column scopes**:
- `scope=trip_info`: Returns the 13 trip-level columns above
- `scope=catch_info`: Returns the 6 catch-level columns above
- No scope parameter: Returns all 18 columns

**Discovering Field Definitions**:

Instead of hardcoding field names, use the metadata endpoints to programmatically discover:
- Field descriptions and meanings
- Data types and units
- Possible values for categorical fields
- Value ranges for numeric fields
- Ontology URLs for semantic web integration

```python
# Example: Discover what fields mean before querying
metadata = get_field_metadata("landings")
for field_name, info in metadata["fields"].items():
    print(f"{field_name}: {info['description']} ({info['data_type']})")
```

See [schema/scopes.py](src/peskas_api/schema/scopes.py) to view or modify scope definitions.  
See [schema/field_metadata.py](src/peskas_api/schema/field_metadata.py) to view or modify field metadata definitions.

### Code Quality

```bash
# Format code
ruff format src/ tests/

# Lint
ruff check src/ tests/

# Type check (if mypy installed)
mypy src/
```

## Deployment

### Docker Build

```bash
docker build -t peskas-api .
docker run -p 8080:8080 \
  -e API_SECRET_KEY=your-key \
  -e GCS_BUCKET_NAME=your-bucket \
  peskas-api
```

### Cloud Run Deployment

Quick deploy:

```bash
# Set variables
export PROJECT_ID=your-gcp-project
export REGION=us-central1
export SERVICE_NAME=peskas-api

# Build and push
gcloud builds submit --tag gcr.io/${PROJECT_ID}/${SERVICE_NAME}

# Deploy
gcloud run deploy ${SERVICE_NAME} \
  --image gcr.io/${PROJECT_ID}/${SERVICE_NAME} \
  --region ${REGION} \
  --platform managed \
  --set-env-vars API_SECRET_KEY=${API_SECRET_KEY} \
  --set-env-vars GCS_BUCKET_NAME=${GCS_BUCKET_NAME} \
  --service-account ${SERVICE_ACCOUNT}@${PROJECT_ID}.iam.gserviceaccount.com \
  --allow-unauthenticated
```

## Architecture Decisions

### Why DuckDB?

- Query Parquet files directly without loading into a database
- Excellent performance for analytical queries
- Zero infrastructure overhead

### Why Schema Flexibility?

The fishery data schema is still evolving. By centralizing column names and dataset types in config files:
- Schema changes require updates in only 1-2 files
- API endpoints remain stable even as data structures change
- Easy to add new dataset types without code refactoring

### Why Parquet + GCS?

- Parquet is columnar, compressed, and efficient for analytical workloads
- GCS provides cheap, reliable storage
- Versioning via raw/validated distinction
- R pipelines can write directly to GCS

## License

Copyright © 2026 WorldFish
