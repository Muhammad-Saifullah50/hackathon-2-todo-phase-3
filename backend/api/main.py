"""Main entry point for the TodoMore API application."""

import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from src.api.routes import health, recurring, search, subtasks, tags, tasks, templates, user
from src.api.routes.chatkit import router as chatkit_router
from src.config import settings
from src.core import setup_logging

# Initialize logging
setup_logging(level=settings.LOG_LEVEL, json_logs=False)

# Import MCP server for mounting (imports also register the tools)
from src.mcp_server.mcp_instance import mcp
from src.mcp_server.tools import task_tools  # noqa: F401


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

# MCP server info endpoint (must be before mount to avoid conflict)
@app.get("/mcp/info", include_in_schema=False)
async def mcp_info() -> HTMLResponse:
    """Return MCP server information and connection details."""
    # Get the server URL from environment or settings
    server_url = os.getenv("VERCEL_URL", f"http://{os.getenv('MCP_HOST', 'localhost')}:{os.getenv('MCP_PORT', '8000')}")
    mcp_url = f"{server_url}/mcp"

    return HTMLResponse(f"""
    <html>
        <head><title>TodoMore MCP Server</title></head>
        <body>
            <h1>TodoMore MCP Server</h1>
            <p>Streamable HTTP MCP server for task management.</p>
            <h2>Connection URL:</h2>
            <code>{mcp_url}</code>
            <h3>Available Tools:</h3>
            <ul>
                <li>add_task - Create a new task</li>
                <li>list_tasks - List tasks with filters</li>
                <li>get_task - Get a specific task</li>
                <li>complete_task - Mark task as complete</li>
                <li>update_task - Update task properties</li>
                <li>delete_task - Delete a task</li>
            </ul>
        </body>
    </html>
    """)

# Mount MCP server at /mcp endpoint for Streamable HTTP transport
# The MCP app handles GET (sse/stream) and POST (messages) for MCP protocol
app.mount("/mcp", mcp.streamable_http_app())


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.main:app", host="0.0.0.0", port=9000, reload=True)