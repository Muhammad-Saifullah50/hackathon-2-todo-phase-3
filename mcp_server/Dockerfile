# syntax=docker/dockerfile:1

FROM python:3.13-slim AS base

# Set working directory
WORKDIR /app

# --- Builder stage: install dependencies into a venv ---
FROM base AS builder

# Install system dependencies required for building wheels (asyncpg, cryptography, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libffi-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt only (for better cache utilization)
COPY --link requirements.txt ./

# Create virtual environment and install dependencies
RUN --mount=type=cache,target=/root/.cache/pip \
    python -m venv .venv && \
    .venv/bin/pip install --upgrade pip setuptools wheel && \
    .venv/bin/pip install -r requirements.txt

# --- Final stage: minimal runtime image ---
FROM base AS final

# Create non-root user
RUN useradd -m mcpuser

# Copy the virtual environment from builder FIRST
COPY --from=builder /app/.venv /app/.venv

# Copy app source code (excluding .env, .git, .venv, etc. via .dockerignore)
COPY --link . .

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Use non-root user
USER mcpuser

# Expose the port FastAPI will listen on
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Default command (can be overridden)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
