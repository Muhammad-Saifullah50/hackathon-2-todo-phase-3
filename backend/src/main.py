"""Main entry point for the TodoMore API application.

Note: MCP server is deployed separately at a different URL.
The chat server connects to the external MCP server URL.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from src.api.routes import health, recurring, search, subtasks, tags, tasks, templates, user
from src.api.routes.chatkit import router as chatkit_router
from src.config import settings
from src.core import setup_logging

# Initialize logging
setup_logging(level=settings.LOG_LEVEL, json_logs=False)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Lifespan events for the application.

    Handles startup and shutdown logic.
    """
    # Startup: Database connection check
    import logging

    from src.database import check_db_connection

    logger = logging.getLogger("uvicorn.error")

    if await check_db_connection():
        logger.info("Database connection verified successfully.")
    else:
        logger.error("Failed to connect to the database on startup.")

    yield
    # Shutdown: Clean up resources


app = FastAPI(
    title="TodoMore API",
    version="1.0.0",
    description="FastAPI backend for TodoMore application",
    lifespan=lifespan,
)

# Attach rate limiter to app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(user.router, prefix="/api/v1", tags=["users"])
app.include_router(tasks.router)
app.include_router(subtasks.router)
app.include_router(search.router)
app.include_router(tags.router)
app.include_router(recurring.router, prefix="/api/v1")
app.include_router(templates.router, prefix="/api/v1")
app.include_router(chatkit_router)  # ChatKit integration endpoint

# Note: MCP server is deployed separately
# The chat server uses settings.MCP_SERVER_URL to connect to the external MCP server


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.main:app", host="0.0.0.0", port=9000, reload=True)