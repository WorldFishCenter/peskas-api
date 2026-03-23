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
from peskas_api.services.api_keys import get_api_key_service
from peskas_api.services.audit import get_audit_service

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
        logger.info(f"MongoDB Database: {settings.mongodb_database}")
    except Exception as e:
        logger.error(f"Failed to load settings during startup: {e}", exc_info=True)
        raise

    yield

    # Cleanup resources
    logger.info("Shutting down...")
    try:
        audit_service = get_audit_service()
        await audit_service.close()
        logger.info("MongoDB connection closed")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}", exc_info=True)


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

    # Request logging middleware with audit logging
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        """Log all requests with timing and status, including audit logging."""
        start_time = time.time()

        # Extract API key info for logging
        api_key = request.headers.get(settings.api_key_header_name)
        api_key_name = "Unknown"
        api_key_id = "N/A"

        if api_key:
            try:
                api_key_service = get_api_key_service()
                key_config = api_key_service.get_key_config(api_key)
                if key_config:
                    api_key_name = key_config.name
                    api_key_id = api_key[:8] + "..." if len(api_key) > 8 else api_key
            except Exception:
                pass  # Don't fail request if API key lookup fails

        client_ip = request.client.host if request.client else "unknown"

        # Log request to stdout
        logger.info(
            f"Request: {request.method} {request.url.path} "
            f"client={client_ip} api_key={api_key_name}"
        )

        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            duration_ms = process_time * 1000

            # Log response to stdout
            logger.info(
                f"Response: {request.method} {request.url.path} "
                f"status={response.status_code} duration={process_time:.3f}s api_key={api_key_name}"
            )

            # Log to MongoDB audit (only for data/metadata endpoints, skip health)
            if api_key and not request.url.path.endswith("/health"):
                try:
                    # Check for dependency override (for tests)
                    if get_audit_service in app.dependency_overrides:
                        audit_service = app.dependency_overrides[get_audit_service]()
                    else:
                        audit_service = get_audit_service()

                    # Extract query parameters
                    query_params = dict(request.query_params)

                    await audit_service.log_data_access(
                        api_key_name=api_key_name,
                        api_key_id=api_key_id,
                        endpoint=request.url.path,
                        method=request.method,
                        client_ip=client_ip,
                        query_params=query_params,
                        status_code=response.status_code,
                        duration_ms=duration_ms,
                    )
                except Exception as e:
                    # Don't fail request if audit logging fails
                    logger.error(f"Failed to log audit event: {e}", exc_info=True)

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
