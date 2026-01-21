"""Custom exceptions and handlers."""

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class DataNotFoundError(Exception):
    """Raised when requested data is not found in GCS."""

    pass


class SchemaError(Exception):
    """Raised when there's a schema-related issue."""

    pass


def register_exception_handlers(app: FastAPI) -> None:
    """Register custom exception handlers."""

    @app.exception_handler(DataNotFoundError)
    async def data_not_found_handler(request: Request, exc: DataNotFoundError):
        logger.warning(
            f"DataNotFoundError: {exc} - Path: {request.url.path} "
            f"Query: {dict(request.query_params)}"
        )
        return JSONResponse(
            status_code=404,
            content={"detail": str(exc)},
        )

    @app.exception_handler(SchemaError)
    async def schema_error_handler(request: Request, exc: SchemaError):
        logger.error(
            f"SchemaError: {exc} - Path: {request.url.path}",
            exc_info=True
        )
        return JSONResponse(
            status_code=400,
            content={"detail": f"Schema error: {exc}"},
        )
