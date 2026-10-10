"""
FastAPI application entry point.

This is the main module that creates and configures the FastAPI app.
"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.openapi.utils import get_openapi
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from peskas_api.api.router import api_router
from peskas_api.core.config import get_settings
from peskas_api.core.exceptions import register_exception_handlers

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Peskas brand files (favicons and logo), shipped inside the package so the wheel has them.
STATIC_DIR = Path(__file__).parent / "static"

# FastAPI's docs helpers take a single favicon URL and no ReDoc options, so the docs
# pages swap in the brand kit's three favicon tags, and give ReDoc's logo (info.x-logo)
# the brand kit's size and clear space: 28px tall (156px wide) with 20px around it.
FAVICON_TAGS = """<link rel="icon" href="/favicon.ico" sizes="32x32">
    <link rel="icon" href="/static/favicon.svg" type="image/svg+xml">
    <link rel="apple-touch-icon" href="/static/apple-touch-icon.png">"""
REDOC_LOGO_THEME = """theme='{"logo": {"gutter": "20px", "maxWidth": "196px"}}'"""


def brand_docs_page(page: HTMLResponse) -> HTMLResponse:
    """Put the brand kit's favicons and ReDoc logo spacing into a FastAPI docs page."""
    html = page.body.decode()
    html = html.replace('<link rel="shortcut icon" href="/favicon.ico">', FAVICON_TAGS)
    html = html.replace("<redoc ", f"<redoc {REDOC_LOGO_THEME} ")
    return HTMLResponse(html)


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
- `catch_taxon`: Optional FAO ASFIS species code filter (comma-separate for multiple, e.g. SKJ,YFT)
- `survey_id`: Optional survey identifier filter
- `scope`: Predefined column set (trip_info, catch_info)
- `limit`: Maximum rows to return (default: 100,000, max: 1,000,000)
        """,
        lifespan=lifespan,
        # /docs and /redoc are defined below, with the Peskas favicon and logo.
        docs_url=None,
        redoc_url=None,
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

    # Docs pages with the Peskas favicon, as in
    # https://fastapi.tiangolo.com/how-to/custom-docs-ui-assets/
    # GET and HEAD, like the built-in docs routes these replace.
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    @app.api_route("/favicon.ico", methods=["GET", "HEAD"], include_in_schema=False)
    async def favicon():
        return FileResponse(STATIC_DIR / "favicon.ico")

    @app.api_route("/docs", methods=["GET", "HEAD"], include_in_schema=False)
    async def swagger_ui_html():
        return brand_docs_page(
            get_swagger_ui_html(
                openapi_url=app.openapi_url,
                title=app.title + " - Swagger UI",
                oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
                swagger_favicon_url="/favicon.ico",
            )
        )

    @app.api_route(
        app.swagger_ui_oauth2_redirect_url, methods=["GET", "HEAD"], include_in_schema=False
    )
    async def swagger_ui_redirect():
        return get_swagger_ui_oauth2_redirect_html()

    @app.api_route("/redoc", methods=["GET", "HEAD"], include_in_schema=False)
    async def redoc_html():
        return brand_docs_page(
            get_redoc_html(
                openapi_url=app.openapi_url,
                title=app.title + " - ReDoc",
                redoc_favicon_url="/favicon.ico",
            )
        )

    # ReDoc's logo, as in https://fastapi.tiangolo.com/how-to/extending-openapi/
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
        )
        openapi_schema["info"]["x-logo"] = {
            "url": "/static/peskas-logo.svg",
            "altText": "Peskas",
            "href": "https://peskas.org",
        }
        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = custom_openapi

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
