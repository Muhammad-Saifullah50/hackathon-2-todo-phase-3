# Stage 1: Builder
FROM python:3.13-slim AS builder

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.5.10 /uv /bin/uv

# Copy dependency definition files
COPY pyproject.toml uv.lock ./

# Install dependencies (production only)
# --frozen: Use uv.lock exactly
# --no-dev: Exclude development dependencies
# --compile: Bytecode compile for faster startup
RUN uv sync --frozen --no-dev --compile

# Stage 2: Runtime
FROM python:3.13-slim

WORKDIR /app

# Install curl for health check
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy uv (optional, but useful for uv run)
COPY --from=ghcr.io/astral-sh/uv:0.5.10 /uv /bin/uv

# Copy the environment from builder
# uv creates the virtual environment in .venv by default
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY . .

# Create a non-root user
RUN adduser --disabled-password --gecos '' apiuser
USER apiuser

# Ensure the virtual environment is in the PATH
ENV PATH="/app/.venv:$PATH"

EXPOSE 8000

# Run with uv run (or directly since PATH is set)
# Using uv run is explicit and safer if env varies
CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
