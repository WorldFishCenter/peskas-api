# Peskas Multi-country Fishery Data API

A service that makes small-scale fishery survey data available for download and analysis. The data describes **fishing trips** (when and where people fished, with what gear) and the **catches** recorded on those trips (species, weight, price, and size).

This document is written for two audiences:

- **Data users** (researchers, analysts, programme staff) — start with [What data is available?](#what-data-is-available) and the [Field reference](#field-reference).
- **Developers** — jump to [API reference](#api-reference), [Integration guide](#integration-guide), or [For developers](#for-developers).

## Table of Contents

- [What data is available?](#what-data-is-available)
- [Understanding the data structure](#understanding-the-data-structure)
- [Field reference](#field-reference)
- [Getting data](#getting-data)
- [API reference](#api-reference)
- [Integration guide](#integration-guide)
- [For developers](#for-developers)
- [Configuration](#configuration)
- [Deployment](#deployment)
- [Architecture decisions](#architecture-decisions)
- [License](#license)

---

## What data is available?

The API currently exposes one dataset type: **landings** — fish landing records that combine trip and catch information.

| Aspect | Details |
|--------|---------|
| **Dataset** | `landings` — fishing trips with associated catch records |
| **Countries** | Multi-country; specify with the `country` parameter (e.g. `zanzibar`, `timor`) |
| **Status** | `validated` (default, quality-checked) or `raw` (pre-validation) |
| **Format** | CSV (default, opens in Excel) or JSON |
| **Columns** | 22 fields per record (see [Field reference](#field-reference)) |

Each row in the dataset represents **one catch record** linked to a fishing trip. Trip-level information (date, location, gear, etc.) is repeated on every row that belongs to the same trip. If a trip reported three species, there will be three rows with the same `trip_id` but different catch details.

---

## Understanding the data structure

The 22 columns fall into two logical groups:

**Trip-level information** (16 columns) — describes the fishing trip as a whole: when it happened, where the catch was landed, administrative location, number of fishers, duration, gear, vessel, habitat, whether any catch was recorded, and trip totals.

**Catch-level information** (8 columns) — describes an individual catch within the trip: species, scientific name, size, weight, and price.

Both groups share `survey_id` and `trip_id` as linking fields, so you can join or aggregate catch rows by trip.

### Choosing which columns to download

You do not always need all 22 columns. Use the `scope` parameter to request a subset:

| Scope | Columns returned | Best for |
|-------|------------------|----------|
| `trip_info` | 16 trip-level columns | Trip summaries, fleet activity, spatial patterns by landing site or district |
| `catch_info` | 8 catch-level columns | Species composition, catch weights and prices, length distributions |
| *(no scope)* | All 22 columns | Full dataset export |

### Looking up field definitions

Every field has a plain-language description, data type, units, and (where applicable) links to standard ontologies (e.g. AQFO, FAO ASFIS). You can browse these without writing code:

```bash
# All field definitions for the landings dataset
curl -H "X-API-Key: your-key" \
  "http://localhost:8000/api/v1/metadata/landings"

# Definitions for trip-level fields only
curl -H "X-API-Key: your-key" \
  "http://localhost:8000/api/v1/metadata/landings?scope=trip_info"

# Definition of a single field
curl -H "X-API-Key: your-key" \
  "http://localhost:8000/api/v1/metadata/landings/fields/catch_kg"
```

The interactive API docs at `/docs` also list all fields and their metadata.

---

## Field reference

### Trip-level fields (16 columns)

| Field | Description | Notes |
|-------|-------------|-------|
| `survey_id` | Identifier of the survey that collected this record | Text |
| `trip_id` | Unique identifier for the fishing trip | Text |
| `landing_date` | Date when the catch was landed | Format: YYYY-MM-DD |
| `gaul_1_code` | GAUL level 1 administrative code (state/province level) | See [GAUL dataset](https://data.apps.fao.org/catalog/dataset/34f97afc-6218-459a-971d-5af1162d318a) |
| `gaul_1_name` | Name of the GAUL level 1 administrative unit | e.g. Unguja North |
| `gaul_2_code` | GAUL level 2 administrative code (district level) | See [GAUL dataset](https://data.apps.fao.org/catalog/dataset/60b23906-f21a-49ef-8424-f3645e70264e) |
| `gaul_2_name` | Name of the GAUL level 2 administrative unit | e.g. District A |
| `landing_site` | Name of the landing site where the catch was recorded | May differ from the vessel's home port |
| `n_fishers` | Number of people actively fishing on the trip | Integer ≥ 1 |
| `trip_duration_hrs` | Duration of the fishing trip | Hours |
| `gear` | Type of fishing gear used | e.g. hand_line, net, trap, spear, longline, trawl |
| `vessel_type` | Type of vessel used | e.g. outrigger, dhow, canoe |
| `catch_habitat` | Habitat where fishing took place | e.g. reef, pelagic, demersal, coastal, offshore |
| `catch_outcome` | Whether the trip resulted in any catch | `1` = catch recorded, `0` = no catch |
| `tot_catch_kg` | Total weight of all catches on the trip | kg (sum of all `catch_kg` for the trip) |
| `tot_catch_price` | Total price of all catches on the trip | Local currency |

### Catch-level fields (8 columns)

| Field | Description | Notes |
|-------|-------------|-------|
| `survey_id` | Survey identifier | Linking field (same as trip-level) |
| `trip_id` | Trip identifier | Linking field (same as trip-level) |
| `catch_taxon` | FAO ASFIS 3-alpha species code | e.g. SKJ, MZZ — see [FAO ASFIS](https://www.fao.org/fishery/en/collection/asfis) |
| `scientific_name` | Full binomial scientific name of the species | e.g. Katsuwonus pelamis |
| `n_catch` | Catch sequence number within the trip | Distinct taxon × size-class combinations |
| `length_cm` | Length associated with the catch record | cm; may represent a length class or measured length |
| `catch_kg` | Weight of this catch record | kg |
| `catch_price` | Price of this catch record | Local currency |

Schema definitions are maintained in [schema/field_metadata.py](src/peskas_api/schema/field_metadata.py) and [schema/scopes.py](src/peskas_api/schema/scopes.py).

---

## Getting data

To download data you need:

1. **An API key** — included in every request as the `X-API-Key` header.
2. **A country** — the only required parameter (e.g. `country=zanzibar`).

Optional filters let you narrow the download:

| Filter | What it does | Example |
|--------|--------------|---------|
| `status` | Raw or validated data | `status=validated` (default) |
| `date_from` / `date_to` | Date range on landing date | `date_from=2025-01-01&date_to=2025-12-31` |
| `gaul_1` / `gaul_2` | Filter by administrative area | `gaul_1=1696` |
| `catch_taxon` | Filter by species code | `catch_taxon=SKJ` |
| `survey_id` | Filter by survey | `survey_id=survey_001` |
| `scope` | Trip-only or catch-only columns | `scope=trip_info` |
| `format` | Output format | `format=json` (default is CSV) |

**Example — download validated Zanzibar data as CSV** (opens in Excel):

```bash
curl -H "X-API-Key: your-key" \
  "http://localhost:8000/api/v1/data/landings?country=zanzibar" \
  -o landings_zanzibar.csv
```

**Example — trip summaries only, filtered by date**:

```bash
curl -H "X-API-Key: your-key" \
  "http://localhost:8000/api/v1/data/landings?country=zanzibar&scope=trip_info&date_from=2025-01-01&date_to=2025-06-30" \
  -o trips_zanzibar.csv
```

Filters can be combined. All filters use AND logic — a row must match every filter you specify.

---

## API reference

### Authentication

All data and metadata endpoints require an API key:

```bash
curl -H "X-API-Key: your-secret-key" \
  "http://localhost:8000/api/v1/data/landings?country=zanzibar"
```

### Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/v1/health` | No | Health check |
| GET | `/api/v1/data/landings` | Yes | Fish landing records |
| GET | `/api/v1/metadata` | Yes | List dataset types with metadata |
| GET | `/api/v1/metadata/{dataset_type}` | Yes | Field metadata for a dataset |
| GET | `/api/v1/metadata/{dataset_type}/fields/{field_name}` | Yes | Metadata for one field |

### Query parameters

**Required**:

- `country` — Country identifier (e.g. `zanzibar`, `timor`)

**Optional**:

- `status` — `raw` or `validated` (default: `validated`)
- `date_from` / `date_to` — Date range `YYYY-MM-DD` (inclusive)
- `gaul_1` / `gaul_2` — GAUL administrative code filters
- `catch_taxon` — FAO ASFIS species code (e.g. `MZZ`, `SKJ`)
- `survey_id` — Survey identifier
- `scope` — `trip_info` or `catch_info`
- `limit` — Max rows (default: 100,000; max: 1,000,000)
- `format` — `csv` (default) or `json`

### Examples

**Validated landings for Zanzibar (CSV)**:

```bash
curl -H "X-API-Key: your-key" \
  "http://localhost:8000/api/v1/data/landings?country=zanzibar"
```

**Raw data with date filter (JSON)**:

```bash
curl -H "X-API-Key: your-key" \
  "http://localhost:8000/api/v1/data/landings?country=zanzibar&status=raw&date_from=2025-02-01&date_to=2025-02-28&format=json"
```

**Filter by region and species**:

```bash
curl -H "X-API-Key: your-key" \
  "http://localhost:8000/api/v1/data/landings?country=zanzibar&gaul_1=1696&catch_taxon=SKJ&format=json"
```

**Catch-level columns only**:

```bash
curl -H "X-API-Key: your-key" \
  "http://localhost:8000/api/v1/data/landings?country=zanzibar&scope=catch_info"
```

**Combined filters**:

```bash
curl -H "X-API-Key: your-key" \
  "http://localhost:8000/api/v1/data/landings?country=zanzibar&gaul_1=1696&gaul_2=16961&catch_taxon=SKJ&survey_id=survey_001&date_from=2025-02-01&scope=trip_info&format=json"
```

### Response formats

**CSV** (default):

```csv
trip_id,landing_date,gaul_1_code,gaul_1_name,landing_site,catch_taxon,catch_kg
trip_001,2023-01-15,1696,Unguja,Nungwi,SKJ,45.2
trip_002,2023-01-16,1696,Unguja,Mkokotoni,MZZ,32.8
```

**JSON** (`format=json`):

```json
{
  "data": [
    {
      "trip_id": "trip_001",
      "landing_date": "2023-01-15T00:00:00",
      "gaul_1_code": "1696",
      "gaul_1_name": "Unguja",
      "landing_site": "Nungwi",
      "catch_taxon": "SKJ",
      "catch_kg": 45.2
    }
  ]
}
```

### Metadata response

Field metadata includes descriptions, data types, units, possible values, value ranges, examples, ontology URLs (AQFO, FAO ASFIS, GAUL), and reference documentation links.

### Error codes

| Code | Meaning | Action |
|------|---------|--------|
| 200 | Success | Process the response |
| 400 | Bad Request | Check parameter values |
| 401 | Unauthorized | Verify API key is present |
| 403 | Forbidden | Check API key validity |
| 404 | Not Found | No data for the specified filters |
| 422 | Validation Error | Check required parameters |
| 500 | Server Error | Retry with exponential backoff |

### Rate limiting and best practices

No rate limits are currently enforced. Recommendations:

- Use `scope` to request only the columns you need
- Use `date_from` / `date_to` for incremental downloads
- Prefer CSV for large exports (~30% smaller than JSON)
- Use the `limit` parameter to control response size
- Implement retry with backoff for server errors (500+)

---

## Integration guide

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
        headers={"X-API-Key": API_KEY},
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
        headers={"X-API-Key": API_KEY},
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

    response = requests.get(url, headers={"X-API-Key": API_KEY})
    response.raise_for_status()
    return response.json()

# Example: Discover available fields
metadata = get_field_metadata("landings")
print("Available fields:")
for field_name, field_info in metadata["fields"].items():
    print(f"  {field_name}: {field_info['description']}")
    if field_info.get("unit"):
        print(f"    Unit: {field_info['unit']}")

# Example usage: Fetch data
df = get_landings_csv(
    country="zanzibar",
    date_from="2023-01-01",
    date_to="2023-12-31",
    gaul_1="1696",
    scope="trip_info",
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
get_landings_data <- function(country, ...) {
  params <- list(country = country, ...)

  response <- GET(
    paste0(API_URL, "/data/landings"),
    query = params,
    add_headers("X-API-Key" = API_KEY),
  )

  stop_for_status(response)

  content <- content(response, "text", encoding = "UTF-8")
  read.csv(text = content, stringsAsFactors = FALSE)
}

#' Get field metadata from Peskas API
get_field_metadata <- function(dataset_type = "landings", field_name = NULL, scope = NULL) {
  if (!is.null(field_name)) {
    url <- paste0(API_URL, "/metadata/", dataset_type, "/fields/", field_name)
  } else {
    url <- paste0(API_URL, "/metadata/", dataset_type)
    if (!is.null(scope)) {
      url <- paste0(url, "?scope=", scope)
    }
  }

  response <- GET(url, add_headers("X-API-Key" = API_KEY))
  stop_for_status(response)
  fromJSON(content(response, "text"))
}

df <- get_landings_data(
  country = "zanzibar",
  date_from = "2023-01-01",
  date_to = "2023-12-31",
  gaul_1 = "1696",
  scope = "trip_info",
)
```

### JavaScript/TypeScript Integration

```typescript
interface LandingsParams {
  country: string;
  status?: "raw" | "validated";
  date_from?: string;
  date_to?: string;
  gaul_1?: string;
  gaul_2?: string;
  catch_taxon?: string;
  survey_id?: string;
  scope?: "trip_info" | "catch_info";
  limit?: number;
  format?: "csv" | "json";
}

class PeskasAPIClient {
  constructor(
    private apiUrl: string,
    private apiKey: string,
  ) {}

  async getLandings(params: LandingsParams): Promise<Record<string, unknown>[]> {
    const queryParams = new URLSearchParams(
      Object.entries({ ...params, format: "json" })
        .filter(([_, v]) => v !== undefined)
        .map(([k, v]) => [k, String(v)]),
    );

    const response = await fetch(`${this.apiUrl}/data/landings?${queryParams}`, {
      headers: { "X-API-Key": this.apiKey },
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status} ${response.statusText}`);
    }

    return (await response.json()).data;
  }

  async getFieldMetadata(datasetType = "landings", scope?: string) {
    let url = `${this.apiUrl}/metadata/${datasetType}`;
    if (scope) url += `?scope=${scope}`;

    const response = await fetch(url, {
      headers: { "X-API-Key": this.apiKey },
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status} ${response.statusText}`);
    }

    return response.json();
  }
}

const client = new PeskasAPIClient("http://localhost:8000/api/v1", "your-api-key");
const data = await client.getLandings({
  country: "zanzibar",
  scope: "trip_info",
  limit: 1000,
});
```

### Error handling

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
                timeout=30,
            )
            response.raise_for_status()
            return pd.read_csv(StringIO(response.text))

        except HTTPError as e:
            if e.response.status_code in [400, 401, 403, 404, 422]:
                raise
            elif e.response.status_code >= 500 and attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                raise
```

---

## For developers

**Stack**: FastAPI + DuckDB + GCS + Parquet → Cloud Run

**Design principles**:

- **Schema flexibility** — column names and dataset types live in config files, not scattered through code
- **Low cost** — serverless Cloud Run + GCS, no database server
- **Extensible** — add dataset types by updating [schema/dataset_config.py](src/peskas_api/schema/dataset_config.py)

### Quick start

```bash
cd peskas-api
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env   # edit with your settings
pytest -v
uvicorn peskas_api.main:app --reload --port 8000
```

Visit http://localhost:8000/docs (API docs) or http://localhost:8000/api/v1/health (health check).

**Prerequisites**: Python 3.11+, Google Cloud credentials, GCS bucket with Parquet files.

### Project structure

```
peskas-api/
├── src/peskas_api/
│   ├── main.py                  # FastAPI app entry point
│   ├── api/                     # Routes and endpoints
│   │   ├── router.py
│   │   ├── deps.py
│   │   └── endpoints/
│   │       ├── health.py
│   │       ├── datasets.py
│   │       └── metadata.py
│   ├── core/                    # Config, auth, exceptions
│   ├── models/                  # Pydantic schemas
│   ├── services/                # GCS + DuckDB query layer
│   └── schema/                  # Dataset config, scopes, field metadata
├── tests/
├── Dockerfile
└── pyproject.toml
```

Key modules:

- **schema/field_metadata.py** — field descriptions, types, ontology links
- **schema/scopes.py** — trip_info / catch_info column lists
- **schema/dataset_config.py** — dataset type registry
- **services/query.py** — DuckDB querying and CSV streaming

### Running tests

```bash
pytest -v
pytest tests/test_auth.py -v
pytest --cov=peskas_api --cov-report=html
```

### Code quality

```bash
ruff format src/ tests/
ruff check src/ tests/
mypy src/   # if installed
```

---

## Configuration

Create a `.env` file (see [.env.example](.env.example)):

```bash
# Required
API_SECRET_KEY=your-secure-random-string
GCS_BUCKET_NAME=your-gcs-bucket-name

# Optional
DEBUG=false
GCS_PROJECT_ID=your-gcp-project-id
DEFAULT_DATE_COLUMN=landing_date
DEFAULT_STATUS=validated
MAX_ROWS_DEFAULT=100000
MAX_ROWS_LIMIT=1000000
```

### GCS data layout

Parquet files must follow this structure:

```
gs://your-bucket/
  zanzibar/
    raw/
      trips-raw__20260120143613_7c6156d__.parquet
    validated/
      trips-validated__20260120143613_7c6156d__.parquet
```

Pattern: `{country}/{status}/trips-{status}__{YYYYMMDDHHMMSS}_{hash}__.parquet`

When multiple versions exist, the API selects the latest file by timestamp.

---

## Deployment

### Docker

```bash
docker build -t peskas-api .
docker run -p 8080:8080 \
  -e API_SECRET_KEY=your-key \
  -e GCS_BUCKET_NAME=your-bucket \
  peskas-api
```

### Cloud Run

```bash
export PROJECT_ID=your-gcp-project
export REGION=us-central1
export SERVICE_NAME=peskas-api

gcloud builds submit --tag gcr.io/${PROJECT_ID}/${SERVICE_NAME}

gcloud run deploy ${SERVICE_NAME} \
  --image gcr.io/${PROJECT_ID}/${SERVICE_NAME} \
  --region ${REGION} \
  --platform managed \
  --set-env-vars API_SECRET_KEY=${API_SECRET_KEY} \
  --set-env-vars GCS_BUCKET_NAME=${GCS_BUCKET_NAME} \
  --service-account ${SERVICE_ACCOUNT}@${PROJECT_ID}.iam.gserviceaccount.com \
  --allow-unauthenticated
```

---

## Architecture decisions

### Why DuckDB?

Queries Parquet files directly without loading into a database. Strong analytical performance with zero database infrastructure.

### Why schema flexibility?

The fishery data schema is still evolving. Centralizing column names in config files means schema changes touch one or two files, endpoints stay stable, and new dataset types do not require refactoring.

### Why Parquet + GCS?

Columnar, compressed storage suited to analytical workloads. GCS is cheap and reliable. Raw/validated versioning is built into the folder structure. R pipelines can write directly to GCS.

---

## License

Copyright © 2026 WorldFish
