"""MCP Server entry point for Vercel deployment.

Deploy this directory as a separate Vercel project.
Tools are defined locally in tools.py (no backend dependency).
"""

import os
import contextlib
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mcp.server.fastmcp import FastMCP

# Import environment setup
from dotenv import load_dotenv

# Load .env from current directory or backend directory
env_path = os.path.join(os.path.dirname(__file__), ".env")
backend_env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend", ".env")

if os.path.exists(env_path):
    load_dotenv(env_path)
    print(f"✅ Loaded env from {env_path}")
elif os.path.exists(backend_env_path):
    load_dotenv(backend_env_path)
    print(f"✅ Loaded env from {backend_env_path}")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifespan for MCP server."""
    print("MCP Server starting up...")
    async with contextlib.AsyncExitStack() as stack:
        # CRITICAL: Start the session manager task group for streamable HTTP
        # This is required when mounting the app inside FastAPI
        await stack.enter_async_context(mcp.session_manager.run())
        yield
    print("MCP Server shutting down...")


# Create FastAPI app for Vercel
# Disable redirect_slashes to prevent 307 redirects that trigger Vercel 421 errors
app = FastAPI(
    title="MCP Task Server",
    lifespan=lifespan,
    redirect_slashes=False,
)

# CORS for MCP clients
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", frontend_url, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Mcp-Session-Id"],
)

# Create MCP server instance with stateless configuration for serverless/production
mcp = FastMCP(
    "Task Management Server",
    stateless_http=True,
    json_response=True,
    streamable_http_path="/",  # Map internal routes to mount point root
)


# Import tools from local tools.py
from tools import (
    add_task as _add_task,
    list_tasks as _list_tasks,
    complete_task as _complete_task,
    delete_task as _delete_task,
    update_task as _update_task,
)


# Register tools with MCP server
@mcp.tool()
async def add_task(
    title: str,
    description: str | None = None,
    due_date: str | None = None,
    priority: str = "medium",
    tags: list[str] | None = None,
    user_id: str = "default_user",
):
    """Add a new task to the user's task list."""
    return await _add_task(
        title=title,
        description=description,
        due_date=due_date,
        priority=priority,
        tags=tags,
        user_id=user_id,
    )


@mcp.tool()
async def list_tasks(
    status: str | None = None,
    priority: str | None = None,
    tags: list[str] | None = None,
    user_id: str = "default_user",
):
    """List tasks with optional filters."""
    return await _list_tasks(
        status=status,
        priority=priority,
        tags=tags,
        user_id=user_id,
    )


@mcp.tool()
async def complete_task(task_id: str, user_id: str = "default_user"):
    """Mark a task as complete."""
    return await _complete_task(task_id=task_id, user_id=user_id)


@mcp.tool()
async def delete_task(task_id: str, user_id: str = "default_user"):
    """Delete a task (soft delete)."""
    return await _delete_task(task_id=task_id, user_id=user_id)


@mcp.tool()
async def update_task(
    task_id: str,
    title: str | None = None,
    description: str | None = None,
    priority: str | None = None,
    due_date: str | None = None,
    user_id: str = "default_user",
):
    """Update an existing task."""
    return await _update_task(
        task_id=task_id,
        title=title,
        description=description,
        priority=priority,
        due_date=due_date,
        user_id=user_id,
    )


# Mount MCP at root (standalone style for separate Vercel project)
# This avoids the /mcp to /mcp/ redirect that triggers 421 Misdirected Request errors on Vercel
app.mount("/", mcp.streamable_http_app())


@app.get("/health")
async def health():
    """Health check."""
    return {"status": "healthy"}


# Export app for Vercel
vercel_app = app
