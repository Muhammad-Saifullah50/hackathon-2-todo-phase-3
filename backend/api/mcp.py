"""MCP Server entry point for Vercel deployment.

This is a standalone MCP server that can be deployed to Vercel separately
from the main API. Deploy this as a separate Vercel project for proper
MCP server isolation in serverless environments.

Usage:
    1. Deploy this file as a separate Vercel project
    2. Set the VERCEL_URL env var to get your deployment URL
    3. Update the main API's MCP_SERVER_URL to point to this deployment
"""

import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mcp.server.fastmcp import FastMCP

# Import environment setup
from dotenv import load_dotenv

# Load .env from backend directory
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
if os.path.exists(env_path):
    load_dotenv(env_path)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifespan for MCP server."""
    print("MCP Server starting up...")
    yield
    print("MCP Server shutting down...")


# Create FastAPI app for Vercel
app = FastAPI(
    title="MCP Task Server",
    lifespan=lifespan,
)

# CORS for MCP clients (allow your frontend domain)
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create MCP server instance
mcp = FastMCP("Task Management Server")


# Import tools to register them with MCP server
# This must happen AFTER mcp is created
from src.mcp_server.tools.task_tools import (
    add_task as _add_task,
    list_tasks as _list_tasks,
    complete_task as _complete_task,
    delete_task as _delete_task,
    update_task as _update_task,
)


# Register tools with MCP server - wrapper functions to inject user_id
@mcp.tool()
async def add_task(
    title: str,
    description: str | None = None,
    due_date: str | None = None,
    priority: str = "medium",
    tags: list[str] | None = None,
    user_id: str = "default_user",
):
    """Add a new task to the user's task list.

    Args:
        title: Task title (1-100 characters, required)
        description: Optional task description (max 500 characters)
        due_date: Optional due date in natural language (e.g., "tomorrow", "next Friday")
        priority: Task priority level - "low", "medium", or "high" (default: "medium")
        tags: Optional list of tag names to apply
        user_id: User ID for task ownership
    """
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
    """List tasks with optional filters.

    Args:
        status: Filter by status - "pending" or "completed"
        priority: Filter by priority - "low", "medium", or "high"
        tags: Filter by tag names
        user_id: User ID for filtering tasks
    """
    return await _list_tasks(
        status=status,
        priority=priority,
        tags=tags,
        user_id=user_id,
    )


@mcp.tool()
async def complete_task(task_id: str, user_id: str = "default_user"):
    """Mark a task as complete.

    Args:
        task_id: The ID of the task to complete
        user_id: User ID for task ownership
    """
    return await _complete_task(task_id=task_id, user_id=user_id)


@mcp.tool()
async def delete_task(task_id: str, user_id: str = "default_user"):
    """Delete a task (soft delete).

    Args:
        task_id: The ID of the task to delete
        user_id: User ID for task ownership
    """
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
    """Update an existing task.

    Args:
        task_id: The ID of the task to update
        title: New task title
        description: New task description
        priority: New priority level
        due_date: New due date
        user_id: User ID for task ownership
    """
    return await _update_task(
        task_id=task_id,
        title=title,
        description=description,
        priority=priority,
        due_date=due_date,
        user_id=user_id,
    )


# Mount MCP at /mcp endpoint for Streamable HTTP transport
app.mount("/mcp", mcp.streamable_http_app())


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "MCP Task Server",
        "endpoints": {
            "mcp": "/mcp",
            "health": "/health",
        }
    }


@app.get("/health")
async def health():
    """Health check."""
    return {"status": "healthy"}


# Export app for Vercel
vercel_app = app

