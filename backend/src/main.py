"""Main entry point for the Todoly API application."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import health, recurring, search, subtasks, tags, tasks, templates, user
from src.api.routes.chatkit import router as chatkit_router
from src.config import settings


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
    title="Todoly API",
    version="1.0.0",
    description="FastAPI backend for Todoly application",
    lifespan=lifespan,
)

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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)