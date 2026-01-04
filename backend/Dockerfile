# syntax=docker/dockerfile:1

FROM python:3.13-slim AS base

# Set working directory
WORKDIR /app

# Create non-root user and group for security
RUN addgroup --system appuser && adduser --system --ingroup appuser appuser

# --- Builder stage: install dependencies only ---
FROM base AS builder

# Install uv (universal Python package manager)
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir uv

# Copy dependency files only (use --link for buildkit performance)
COPY --link pyproject.toml requirements.txt ./

# Install dependencies using uv (production only)
RUN --mount=type=cache,target=/root/.cache/pip \
    uv pip install --system --requirement requirements.txt

# --- Final stage: minimal runtime image ---
FROM base AS final

# Copy installed dependencies from builder
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code (excluding files in .dockerignore)
COPY --link . .

# Set environment variables for production
ENV PYTHONUNBUFFERED=1
ENV UVICORN_WORKERS=4

# Switch to non-root user
USER appuser

# Expose FastAPI port
EXPOSE 9000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:9000/health')" || exit 1

# Start FastAPI app with Uvicorn
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "9000", "--workers", "4"]
