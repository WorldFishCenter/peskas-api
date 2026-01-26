"""
FastAPI application entry point.

This is the main module that creates and configures the FastAPI app.
"""

import logging
from contextlib import asynccontextmanager

import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from peskas_api.api.router import api_router
from peskas_api.core.config import get_settings
from peskas_api.core.exceptions import register_exception_handlers

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup/shutdown."""
    try:
        settings = get_settings()
        logger.info(f"Starting {settings.api_title} v{settings.api_version}")
        logger.info(f"GCS Bucket: {settings.gcs_bucket_name}")
    except Exception as e:
        logger.error(f"Failed to load settings during startup: {e}", exc_info=True)
        raise

    yield

    logger.info("Shutting down...")


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

- `country`: Required country identifier (e.g., zanzibar, timor)
- `status`: raw or validated (default: validated)
- `date_from`, `date_to`: Optional date range (YYYY-MM-DD)
- `gaul_1`: Optional GAUL level 1 administrative code filter
- `gaul_2`: Optional GAUL level 2 administrative code filter
- `catch_taxon`: Optional FAO ASFIS species code filter
- `survey_id`: Optional survey identifier filter
- `scope`: Predefined column set (trip_info, catch_info)
- `limit`: Maximum rows to return (default: 100,000, max: 1,000,000)
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

    # Request logging middleware
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        """Log all requests with timing and status."""
        start_time = time.time()
        
        # Log request
        logger.info(
            f"Request: {request.method} {request.url.path} "
            f"client={request.client.host if request.client else 'unknown'}"
        )
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Log response
            logger.info(
                f"Response: {request.method} {request.url.path} "
                f"status={response.status_code} duration={process_time:.3f}s"
            )
            
            # Add timing header
            response.headers["X-Process-Time"] = str(process_time)
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"Error: {request.method} {request.url.path} "
                f"exception={type(e).__name__} duration={process_time:.3f}s",
                exc_info=True
            )
            raise

    # Mount API routes
    try:
        app.include_router(api_router, prefix=settings.api_prefix)
    except Exception as e:
        logger.error(f"Failed to mount API routes: {e}", exc_info=True)
        raise

    return app


# Create app instance - this runs at import time
# If this fails, uvicorn won't be able to start
try:
    app = create_app()
    logger.info("FastAPI app created successfully")
except Exception as e:
    logger.error(f"Failed to create FastAPI app: {e}", exc_info=True)
    # Re-raise so uvicorn sees the error
    raise
