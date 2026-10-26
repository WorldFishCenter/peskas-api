<picture>
  <source media="(prefers-color-scheme: dark)" srcset=".github/images/peskas-logo-dark.svg">
  <img src=".github/images/peskas-logo.svg" alt="Peskas" height="48">
</picture>

# Peskas Fishery Data API

Programmatic access to the small-scale fisheries landing records collected by Peskas.

Base URL: `https://api.peskas.org/api/v1`. Interactive documentation: [api.peskas.org/docs](https://api.peskas.org/docs).

## What it is

The Peskas Fishery Data API serves landing records from the four Peskas country pipelines (Kenya, Mozambique, Timor-Leste and Zanzibar), and the same data summed up by district and month. It is for researchers, analysts and programme staff who want the data in R, Python, a spreadsheet or their own systems. Downloading data needs an API key.

## What you can do

- Download a country's landing records as CSV or JSON.
- Choose checked records (`validated`, the default) or all records as collected (`raw`).
- Filter by landing date, administrative region, species or survey form.
- Ask for trip-level or catch-level columns only.
- Download monthly figures per district (`/data/district-months`), as the country dashboards show them.
- Look up what each field means, its units and its allowed values.

## Get access

Send your key in the `X-API-Key` header. To get one, write to <peskas.platform@gmail.com>. The `/metadata` endpoints, which describe the fields, need no key.

No code? Sign in to the [Peskas Management Platform](https://validation.peskas.org) and use **Data Tools > Data Download**, which downloads from this API.

## First requests

Each example downloads validated Zanzibar landings from 1 January 2025 onwards. Store your key in the `PESKAS_API_KEY` environment variable first.

curl:

```bash
curl -H "X-API-Key: $PESKAS_API_KEY" \
  "https://api.peskas.org/api/v1/data/landings?country=zanzibar&date_from=2025-01-01&limit=1000000" \
  -o landings_zanzibar.csv
```

R, with httr2:

```r
library(httr2)

resp <- request("https://api.peskas.org/api/v1/data/landings") |>
  req_headers(`X-API-Key` = Sys.getenv("PESKAS_API_KEY")) |>
  req_url_query(country = "zanzibar", date_from = "2025-01-01", limit = 1000000) |>
  req_perform()
landings <- read.csv(text = resp_body_string(resp))
```

Python, with requests:

```python
import io
import os

import pandas as pd
import requests

resp = requests.get(
    "https://api.peskas.org/api/v1/data/landings",
    headers={"X-API-Key": os.environ["PESKAS_API_KEY"]},
    params={"country": "zanzibar", "date_from": "2025-01-01", "limit": 1000000},
    timeout=300,
)
resp.raise_for_status()
landings = pd.read_csv(io.StringIO(resp.text))
```

Monthly figures per district work the same way, at `/data/district-months`:

```bash
curl -H "X-API-Key: $PESKAS_API_KEY" \
  "https://api.peskas.org/api/v1/data/district-months?country=zanzibar&date_from=2025-01-01" \
  -o district_months_zanzibar.csv
```

`country` is one of `kenya`, `mozambique`, `timor` or `zanzibar`. Add `status=raw` for records before checks, `format=json` for JSON, `gaul_2=106434,106432` for some districts only, or `scope=trip_info` / `scope=catch_info` for fewer columns. The [docs page](https://api.peskas.org/docs) lists every endpoint, parameter and error code, and lets you try requests in the browser.

## What the data contains

Each row is one catch from one landing (a boat's return to shore with its catch). A trip that landed three species has three rows with the same `trip_id`, and the trip details repeat on each row.

There are 23 columns. 17 describe the trip: who collected it, date, place, number of fishers, duration, gear, boat, habitat, whether anything was caught, and trip totals. 8 describe the catch: species, length, weight and price. `survey_id` and `trip_id` appear in both groups, which is how catch rows link to their trip.

[`FIELDS.md`](FIELDS.md) lists every column of each endpoint. The same descriptions, units, allowed values and links to standards (FAO ASFIS species codes, FAO GAUL administrative regions) are served by the `/metadata/landings` endpoint, which you can also call from the docs page.

`survey_organization` names who collected each record:

| Code | Organization | Country |
|------|--------------|---------|
| `KEFS` | [Kenya Fisheries Service](https://kefs.go.ke/) | Kenya |
| `WCS` | [Wildlife Conservation Society](https://kenya.wcs.org/) | Kenya |
| `ZAFIRI` | Zanzibar Fisheries and Marine Resources Research Institute | Zanzibar |
| `DINAPA` | National Directorate of Fisheries and Aquaculture (formerly ADNAP) | Mozambique |
| `MAF` | [Ministry of Agriculture and Fisheries](https://maf.gov.tl/) | Timor-Leste |

## Monthly figures per district

`/data/district-months` has one row per district and month: 23 columns in four groups.

- **Where and when**: `country`, `month` (its first day), and the region and district as GAUL codes and names. A row is identified by `gaul_2_code` and `month`. Timor-Leste's rows are its municipalities instead, so `gaul_2_code` is empty there, except on Atauro's own row.
- **What enumerators recorded**: `n_submissions` (landings recorded and validated) and averages per trip: fishers, duration, catch, value, price per kg, catch and value per fisher per hour.
- **Whole fleet, GPS tracker method**: estimated trips, catch (tonnes) and revenue, and `sampling_rate`, the share of the district's boats with a tracker.
- **Whole fleet, FAO ARTFISH method**: estimated trips, catch and revenue (`_fao`), and the relative error of the catch and revenue at 90% confidence.

Things to know about these rows:

- **Adding up rows**: totals (`n_submissions` and the `estimated_` columns) can be summed across months and districts. Averages (`mean_` columns) must be weighted by `n_submissions`.
- **Two methods, two estimates**: compare them only on rows where both have a value, as the dashboards do.
- **How sure the estimates are**: the GPS tracker estimate is good with a `sampling_rate` of 0.3 or more, fair from 0.1, weak below. FAO's Toolkit aims for an ARTFISH relative error of 0.15 or less and accepts 0.20; in October 2026 most district-months are well above it.
- **Empty is not zero**: an empty estimate could not be made, for example with fewer than 10 landings recorded. Timor-Leste's estimates come from its own model, not the GPS trackers, and fill every month from 2018.
- **Months with nothing recorded** stay, with `n_submissions` at 0, so gaps in data collection show. **Landings with no district** (a landing site not matched to one) are not in any row.
- **Dates**: `date_from` and `date_to` are compared with each month's first day, so use the first of a month.

[`FIELDS.md`](FIELDS.md) and `/metadata/district-months` describe every column.

## Things to know

- **Row cap**: without `limit`, a request returns at most 100,000 rows and does not say that rows were cut. Set `limit` (up to 1,000,000), or split large downloads by date.
- **Errors versus empty results**: 404 means there is no data file for that country and status, for example a misspelt country. A request whose filters match nothing returns 200 with no rows.
- **Kenya has two programmes that differ**: WCS records no trip duration or length. KEFS weighs the whole catch but identifies species on a sample, so its catch rows are not meant to sum to `tot_catch_kg`. Use `survey_organization` to tell them apart, not `survey_id`, which identifies the survey form.
- **Prices are in local currency** and are not converted between countries.
- **Updates**: the API serves the newest file each country pipeline has published. The pipelines run every two to four days.

## Who runs it

[WorldFish](https://worldfishcenter.org/) runs the Peskas Fishery Data API. The records come from the survey organizations listed above. For questions, write to <peskas.platform@gmail.com>.

## Part of Peskas

Peskas is WorldFish's open-source platform for monitoring small-scale fisheries (https://peskas.org).

- [Peskas Zanzibar](https://zanzibar.peskas.org), [Peskas Kenya](https://peskas-dashboard-kenya.vercel.app/en), [Peskas Mozambique](https://peskas-dashboard-mozambique.vercel.app): country dashboards
- [Peskas Timor-Leste](https://timor.peskas.org): Timor-Leste portal
- [Peskas Coasts](https://coasts.peskas.org): regional comparison across countries
- [Peskas Tracks](https://tracks.peskas.org): app for fishers to see their trips and log catches
- [Peskas Kenya BMU dashboard](https://digitalfisheries.kenya.peskas.org): dashboard for Beach Management Units in Kenya
- [Peskas Management Platform](https://validation.peskas.org): data review and download for survey teams
- Data pipelines: [Kenya](https://github.com/WorldFishCenter/peskas.kenya.data.pipeline), [Zanzibar](https://github.com/WorldFishCenter/peskas.zanzibar.data.pipeline), [Mozambique](https://github.com/WorldFishCenter/peskas.mozambique.data.pipeline), [Timor-Leste](https://github.com/WorldFishCenter/peskas.timor.data.pipeline), [Coasts](https://github.com/WorldFishCenter/peskas.coasts)

## For developers

A FastAPI service on Google Cloud Run. The country pipelines write versioned `trips-raw` and `trips-validated` parquet files to `{country}/{raw|validated}/` in a Google Cloud Storage bucket, and `export_portal()` in [peskas.coasts](https://github.com/WorldFishCenter/peskas.coasts) writes `district-months` files to `{country}/aggregated/`. Each dataset's folder and file name are set in [`schema/dataset_config.py`](src/peskas_api/schema/dataset_config.py); the API picks the newest file by the timestamp in its name ([`services/gcs.py`](src/peskas_api/services/gcs.py)) and queries it with DuckDB ([`services/query.py`](src/peskas_api/services/query.py)). Column definitions live in [`schema/field_metadata.py`](src/peskas_api/schema/field_metadata.py) and the scopes in [`schema/scopes.py`](src/peskas_api/schema/scopes.py).

**Requirements**: Python 3.11+, and Google Cloud credentials that can read the bucket.

**Setup**:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"   # editable install, so /health reports the right version
cp .env.example .env      # set API_SECRET_KEY and GCS_BUCKET_NAME
```

**Test and lint**:

```bash
pytest
ruff check .
ruff format .
```

**Run locally**:

```bash
uvicorn peskas_api.main:app --reload --port 8000
```

Then open http://localhost:8000/docs.

**Deploy**: a push to `main` builds the image and deploys it to the `peskas-api` Cloud Run service in `europe-west1` ([`deploy.yml`](.github/workflows/deploy.yml)). There is no staging service, so open a pull request and run `pytest` before merging.

**Release**: bump `version` in `pyproject.toml` and add a `# peskas-api X.Y.Z` block at the top of [`NEWS.md`](NEWS.md). On a push to `main`, [`release.yml`](.github/workflows/release.yml) turns that block into a GitHub release. It skips the release if the tag already exists, so a forgotten NEWS bump deploys without a release.

**Changing columns**: a landings column added, renamed or reordered is a change in three places: this repo (`field_metadata.py`, `scopes.py`, `tests/test_field_metadata.py`, `NEWS.md`), the four country pipelines, and the Peskas Management Platform. A district-months column is a change here and in peskas.coasts (`api_district_months()` and its test). After any field change, regenerate [`FIELDS.md`](FIELDS.md) with `python -m peskas_api.schema.fields_doc`; a test fails until you do.

**AI-assisted work**: see [`CLAUDE.md`](CLAUDE.md).
