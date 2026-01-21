"""
FastAPI application entry point.

This is the main module that creates and configures the FastAPI app.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from peskas_api.api.router import api_router
from peskas_api.core.config import get_settings
from peskas_api.core.exceptions import register_exception_handlers


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup/shutdown."""
    settings = get_settings()
    print(f"Starting {settings.api_title} v{settings.api_version}")
    print(f"GCS Bucket: {settings.gcs_bucket_name}")

    yield

    print("Shutting down...")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title=settings.api_title,
        version=settings.api_version,
        description="""
API for accessing multi-country small-scale fishery data.

## Authentication

All data endpoints require an API key passed in the `X-API-Key` header.

## Data Format

By default, data is returned as CSV. Use `format=json` for JSON output.

## Filtering

- `country`: Required country code (e.g., TLS, IDN)
- `year`: Required data year
- `status`: raw or validated (default: validated)
- `date_from`, `date_to`: Optional date range within the year
- `fields`: Comma-separated column names
- `scope`: Predefined column set (core, detailed, summary)
        """,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS (configure appropriately for production)
    if settings.debug:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Register exception handlers
    register_exception_handlers(app)

    # Mount API routes
    app.include_router(api_router, prefix=settings.api_prefix)

    return app


app = create_app()
