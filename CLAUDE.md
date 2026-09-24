# peskas-api

FastAPI + DuckDB service that serves the country pipelines' `trips-*` landings parquet from GCS, deployed on Cloud Run. Its main consumer is `peskas-validation` (data downloads and the data explorer). Ecosystem context (other repos, data flow, cross-repo contracts): see PESKAS.md, loaded via CLAUDE.local.md.

## Commands

- Install: `pip install -e ".[dev]"` inside `.venv`. Without the editable install, `peskas_api.__version__` falls back to `0.1.0` (`src/peskas_api/__init__.py`), so `/health` and the OpenAPI docs report the wrong version.
- Test: `pytest`
- Lint/format: `ruff check .` and `ruff format .`
- Run locally: `uvicorn peskas_api.main:app --reload --port 8000` (needs `API_SECRET_KEY` and `GCS_BUCKET_NAME`, see `.env.example`).

## Architecture

- Country pipelines (`export_api_raw/validated`) write `trips-{status}` parquet to `{country}/{raw|validated}/` in the `peskas-api-dev` / `peskas-api-prod` buckets. The service picks the newest file by the timestamp in its versioned filename (`services/gcs.py`) and queries it with DuckDB (`services/query.py`).
- Column names, types and descriptions live in `schema/field_metadata.py`; the `trip_info` / `catch_info` subsets live in `schema/scopes.py`.

## Rules

- Treat a column add, rename or reorder as a change in three places: this repo, the four country pipelines, and `peskas-validation` (its `data-explorer/*.qmd` lessons hard-code column names; `lib/peskas-api.js` and `api/data-download/*` hard-code the filter and scope parameters).
- In this repo a column change touches `schema/field_metadata.py`, `schema/scopes.py`, `tests/test_field_metadata.py`, the README column counts (and its organizations table, for a new `survey_organization` value), and `NEWS.md`. The full field list is served by the `/metadata` endpoints from `field_metadata.py`; the README no longer carries field tables.
- To release, bump `version` in `pyproject.toml` and add a `# peskas-api X.Y.Z` block at the top of `NEWS.md`. Keep the two in sync.

## Gotchas

- A push to `main` deploys straight to production Cloud Run (`.github/workflows/deploy.yml`) and tags a release from the top NEWS block (`release.yml`). There is no staging service; open a PR and run `pytest` before merging.
- `release.yml` skips the release when the tag already exists, so forgetting the NEWS bump deploys silently without a release.
- `docs/` is gitignored: files there are local notes, not published documentation.
