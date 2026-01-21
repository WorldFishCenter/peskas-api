# Multi-stage build for smaller image
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN pip install --no-cache-dir build

# Copy project files
COPY pyproject.toml .
COPY src/ src/

# Build wheel
RUN python -m build --wheel

# Production image
FROM python:3.11-slim

WORKDIR /app

# Install the built wheel
COPY --from=builder /app/dist/*.whl .
RUN pip install --no-cache-dir *.whl && rm *.whl

# Create non-root user first
RUN useradd -m -u 1000 appuser

# Create temp directory for parquet cache with proper permissions
RUN mkdir -p /tmp/peskas_cache && chown appuser:appuser /tmp/peskas_cache

USER appuser

# Expose port
EXPOSE 8080

# Run with uvicorn
CMD ["uvicorn", "peskas_api.main:app", "--host", "0.0.0.0", "--port", "8080"]
