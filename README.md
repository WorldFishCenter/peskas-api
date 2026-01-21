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
- GAUL administrative code filtering
- FAO ASFIS species code filtering
- Column selection via predefined scopes or explicit field lists
- CSV streaming (default) and JSON output

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

### Query Parameters

**Required**:
- `country`: Country identifier (e.g., `zanzibar`)

**Optional**:
- `status`: `raw` or `validated` (default: `validated`)
- `date_from`: Start date `YYYY-MM-DD` (inclusive)
- `date_to`: End date `YYYY-MM-DD` (inclusive)
- `gaul_1`: GAUL level 1 administrative code filter (e.g., `1696`)
- `catch_taxon`: FAO ASFIS species code filter (e.g., `MZZ`, `SKJ`)
- `fields`: Comma-separated column names (e.g., `trip_id,landing_date,catch_kg`)
- `scope`: Predefined column set (`core`, `detailed`, `summary`, `trip`)
- `limit`: Max rows to return (default: 100,000, max: 1,000,000)
- `format`: `csv` (default) or `json`

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

**Get specific columns using scope**:
```bash
curl -H "X-API-Key: your-key" \
  "http://localhost:8000/api/v1/data/landings?country=zanzibar&scope=core"
```

**Get specific fields**:
```bash
curl -H "X-API-Key: your-key" \
  "http://localhost:8000/api/v1/data/landings?country=zanzibar&fields=trip_id,landing_date,catch_kg"
```

**Combined filters**:
```bash
curl -H "X-API-Key: your-key" \
  "http://localhost:8000/api/v1/data/landings?country=zanzibar&gaul_1=1696&catch_taxon=SKJ&date_from=2025-02-01&scope=core&format=json"
```

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

**Core columns**:
- `trip_id`: Trip identifier
- `landing_date`: Date of landing
- `gaul_1_code`, `gaul_1_name`: GAUL level 1 administrative codes
- `catch_taxon`: FAO ASFIS species code
- `catch_kg`: Catch weight in kilograms

**Trip details**:
- `survey_id`: Survey identifier
- `n_fishers`: Number of fishers
- `trip_duration_hrs`: Trip duration in hours
- `gear`: Fishing gear type
- `vessel_type`: Type of vessel

**Catch details**:
- `gaul_2_code`, `gaul_2_name`: GAUL level 2 administrative codes
- `catch_habitat`: Habitat code
- `catch_outcome`: Outcome code
- `n_catch`: Number of catch items
- `length_cm`: Fish length in cm
- `catch_price`: Price in local currency

See [schema/scopes.py](src/peskas_api/schema/scopes.py) for predefined column scopes.

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
