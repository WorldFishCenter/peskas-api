"""Custom exceptions and handlers."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


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
        return JSONResponse(
            status_code=404,
            content={"detail": str(exc)},
        )

    @app.exception_handler(SchemaError)
    async def schema_error_handler(request: Request, exc: SchemaError):
        return JSONResponse(
            status_code=400,
            content={"detail": f"Schema error: {exc}"},
        )
