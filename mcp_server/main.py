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

# Create MCP server instance with stateless configuration for serverless/production
# Note: streamable_http_path should be "/" because we mount the entire app at /mcp
# The MCP protocol endpoints will be available at /mcp/sse, /mcp/message, etc.
mcp = FastMCP(
    "Task Management Server",
    stateless_http=True,
    json_response=True,
    streamable_http_path="/",  # Root of the mounted app (which is at /mcp)
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifespan for MCP server with proper resource management."""
    print("🚀 MCP Server starting up...")
    async with contextlib.AsyncExitStack() as stack:
        # CRITICAL: Start the session manager task group for streamable HTTP
        # This is required when mounting the app inside FastAPI
        await stack.enter_async_context(mcp.session_manager.run())
        print("✅ Session manager started successfully")

        # Initialize database pool on startup
        await get_pool()

        yield

        # Cleanup on shutdown
        await close_pool()
    print("🛑 MCP Server shutting down...")


# Create FastAPI app for Vercel with disabled docs to reduce overhead
# Note: Don't use TrustedHostMiddleware as it causes issues with Vercel's proxy
app = FastAPI(
    title="MCP Task Server",
    lifespan=lifespan,
    redirect_slashes=False,
    docs_url=None,  # Disable swagger UI
    redoc_url=None,  # Disable redoc
    root_path="",  # Important: empty root path for Vercel
)

# CORS for MCP clients (must be added BEFORE mounting MCP)
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins to avoid host header issues
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Mcp-Session-Id", "Content-Type"],
)


# Database imports and setup
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Optional
from dateutil import parser
import asyncpg

# Authentication imports
from auth import extract_user_id_from_authorization

# Database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set")


# Remove asyncpg scheme for asyncpg.connect
def get_db_url() -> str:
    url = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
    return url.replace("+psycopg://", "postgresql://")


# Connection pool configuration (optimized for serverless)
_pool: Optional[asyncpg.Pool] = None
DB_POOL_MIN_SIZE = int(os.getenv("DB_POOL_MIN_SIZE", "1"))
DB_POOL_MAX_SIZE = int(os.getenv("DB_POOL_MAX_SIZE", "5"))
DB_POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "60"))
DB_POOL_MAX_INACTIVE_LIFETIME = int(os.getenv("DB_POOL_MAX_INACTIVE_LIFETIME", "300"))


async def get_pool() -> asyncpg.Pool:
    """Get or create connection pool with production-ready configuration.

    Pool configuration is optimized for serverless environments:
    - Small pool size (1-5 connections) to avoid overwhelming database
    - Short timeouts to handle serverless cold starts
    - Automatic connection cleanup for inactive connections

    Environment variables for tuning:
    - DB_POOL_MIN_SIZE: Minimum pool size (default: 1)
    - DB_POOL_MAX_SIZE: Maximum pool size (default: 5)
    - DB_POOL_TIMEOUT: Command timeout in seconds (default: 60)
    - DB_POOL_MAX_INACTIVE_LIFETIME: Max lifetime for idle connections in seconds (default: 300)
    """
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(
            get_db_url(),
            min_size=DB_POOL_MIN_SIZE,
            max_size=DB_POOL_MAX_SIZE,
            command_timeout=DB_POOL_TIMEOUT,
            max_inactive_connection_lifetime=DB_POOL_MAX_INACTIVE_LIFETIME,
            # Additional serverless optimizations
            server_settings={
                'application_name': 'mcp_task_server',
                'jit': 'off',  # Disable JIT for faster cold starts
            }
        )
        print(f"✅ Database pool created: min={DB_POOL_MIN_SIZE}, max={DB_POOL_MAX_SIZE}, timeout={DB_POOL_TIMEOUT}s")
    return _pool


async def close_pool():
    """Close the connection pool gracefully."""
    global _pool
    if _pool:
        await _pool.close()
        _pool = None
        print("🛑 Database pool closed")


# Register MCP tools
@mcp.tool()
async def add_task(
    title: str,
    authorization: str,
    description: str | None = None,
    due_date: str | None = None,
    priority: str = "medium",
    tags: list[str] | None = None,
) -> dict[str, Any]:
    """Add a new task to the user's task list.

    Args:
        title: Task title (required)
        authorization: Bearer token for authentication (required)
        description: Optional task description
        due_date: Optional due date (ISO format or parseable date string)
        priority: Task priority (low, medium, high)
        tags: Optional list of tag names

    Returns:
        Dictionary with success status, task data, and message
    """
    pool = await get_pool()

    # Authenticate and get user_id
    try:
        user_id = await extract_user_id_from_authorization(authorization, pool)
    except ValueError as e:
        return {"success": False, "error": f"Authentication failed: {str(e)}"}

    async with pool.acquire() as conn:
        async with conn.transaction():
            try:
                # Parse due date with proper timezone handling
                parsed_due_date = None
                if due_date:
                    try:
                        # Parse the date with dateutil parser
                        parsed_due_date = parser.parse(due_date)

                        # If the parsed date is naive (no timezone), assume UTC
                        if parsed_due_date.tzinfo is None:
                            parsed_due_date = parsed_due_date.replace(tzinfo=timezone.utc)
                        else:
                            # Convert to UTC if it has a different timezone
                            parsed_due_date = parsed_due_date.astimezone(timezone.utc)
                    except Exception as e:
                        return {"error": f"Invalid date format '{due_date}': {str(e)}", "success": False}

                # Validate priority
                priority_lower = priority.lower()
                if priority_lower not in ["low", "medium", "high"]:
                    return {
                        "error": f"Invalid priority '{priority}'. Must be 'low', 'medium', or 'high'.",
                        "success": False,
                    }

                # Create task with proper UUID
                task_id = str(uuid.uuid4())
                now = datetime.now(timezone.utc)

                await conn.execute(
                    """
                    INSERT INTO tasks (id, user_id, title, description, priority, due_date, status, created_at, updated_at)
                    VALUES ($1, $2, $3, $4, $5, $6, 'pending', $7, $7)
                    """,
                    task_id, user_id, title, description, priority_lower, parsed_due_date, now
                )

                # Add tags
                task_tags = []
                if tags:
                    for tag_name in tags:
                        tag_id = str(uuid.uuid4())
                        tag_color = "#3B82F6"

                        # Check if tag exists
                        existing = await conn.fetchrow(
                            "SELECT id FROM tags WHERE user_id = $1 AND LOWER(name) = $2",
                            user_id, tag_name.lower()
                        )

                        if existing:
                            current_tag_id = existing["id"]
                        else:
                            current_tag_id = tag_id
                            await conn.execute(
                                "INSERT INTO tags (id, user_id, name, color, created_at) VALUES ($1, $2, $3, $4, $5)",
                                current_tag_id, user_id, tag_name, tag_color, now
                            )

                        # Add tag to task
                        await conn.execute(
                            "INSERT INTO task_tags (task_id, tag_id) VALUES ($1, $2)",
                            task_id, current_tag_id
                        )
                        task_tags.append(tag_name)

                return {
                    "success": True,
                    "task": {
                        "id": task_id,
                        "title": title,
                        "description": description,
                        "status": "pending",
                        "priority": priority_lower,
                        "due_date": parsed_due_date.isoformat() if parsed_due_date else None,
                        "created_at": now.isoformat(),
                        "tags": task_tags,
                    },
                    "message": f"✅ Task '{title}' created successfully",
                }
            except Exception as e:
                return {"error": str(e), "success": False}


@mcp.tool()
async def list_tasks(
    authorization: str,
    status: str | None = None,
    priority: str | None = None,
    tags: list[str] | None = None,
) -> dict[str, Any]:
    """List tasks with optional filters.

    Args:
        authorization: Bearer token for authentication (required)
        status: Filter by status (pending, completed)
        priority: Filter by priority (low, medium, high)
        tags: Filter by tag names (not yet implemented)

    Returns:
        Dictionary with success status, tasks list, and count
    """
    pool = await get_pool()

    # Authenticate and get user_id
    try:
        user_id = await extract_user_id_from_authorization(authorization, pool)
    except ValueError as e:
        return {"success": False, "error": f"Authentication failed: {str(e)}"}

    async with pool.acquire() as conn:
        try:
            # Build query
            query = """
                SELECT t.id, t.user_id, t.title, t.description, t.priority,
                       t.due_date, t.status, t.created_at, t.completed_at,
                       COALESCE(json_agg(json_build_object('id', tags.id, 'name', tags.name)) FILTER (WHERE tags.id IS NOT NULL), '[]') as tags
                FROM tasks t
                LEFT JOIN task_tags tt ON t.id = tt.task_id
                LEFT JOIN tags ON tt.tag_id = tags.id
                WHERE t.user_id = $1 AND t.deleted_at IS NULL
            """
            params = [user_id]
            param_count = 1

            if status:
                param_count += 1
                query += f" AND t.status = ${param_count}"
                params.append(status)

            if priority:
                param_count += 1
                query += f" AND t.priority = ${param_count}"
                params.append(priority)

            query += " GROUP BY t.id ORDER BY t.created_at DESC LIMIT 100"

            rows = await conn.fetch(query, *params)

            tasks_list = []
            for row in rows:
                # Get tags list from JSON
                row_tags = row["tags"]
                if isinstance(row_tags, str):
                    row_tags = json.loads(row_tags)

                tasks_list.append({
                    "id": row["id"],
                    "title": row["title"],
                    "description": row["description"],
                    "status": row["status"],
                    "priority": row["priority"],
                    "due_date": row["due_date"].isoformat() if row["due_date"] else None,
                    "created_at": row["created_at"].isoformat(),
                    "completed_at": row["completed_at"].isoformat() if row["completed_at"] else None,
                    "tags": [t["name"] for t in row_tags if "name" in t],
                })

            return {
                "success": True,
                "tasks": tasks_list,
                "count": len(tasks_list),
                "message": f"Found {len(tasks_list)} task(s)",
            }
        except Exception as e:
            return {"error": str(e), "success": False}


@mcp.tool()
async def complete_task(
    task_id: str,
    authorization: str,
) -> dict[str, Any]:
    """Mark a task as complete.

    Args:
        task_id: ID of the task to complete
        authorization: Bearer token for authentication (required)

    Returns:
        Dictionary with success status, task data, and message
    """
    pool = await get_pool()

    # Authenticate and get user_id
    try:
        user_id = await extract_user_id_from_authorization(authorization, pool)
    except ValueError as e:
        return {"success": False, "error": f"Authentication failed: {str(e)}"}

    async with pool.acquire() as conn:
        async with conn.transaction():
            try:
                # Check task exists
                task = await conn.fetchrow(
                    "SELECT * FROM tasks WHERE id = $1 AND user_id = $2 AND deleted_at IS NULL",
                    task_id, user_id
                )

                if not task:
                    return {"error": f"Task with ID '{task_id}' not found", "success": False}

                if task["status"] == "completed":
                    return {"error": f"Task '{task['title']}' is already completed", "success": False}

                now = datetime.now(timezone.utc)

                await conn.execute(
                    "UPDATE tasks SET status = 'completed', completed_at = $1, updated_at = $1 WHERE id = $2",
                    now, task_id
                )

                return {
                    "success": True,
                    "task": {
                        "id": task_id,
                        "title": task["title"],
                        "status": "completed",
                        "completed_at": now.isoformat(),
                    },
                    "message": f"✅ Task '{task['title']}' marked as complete",
                }
            except Exception as e:
                return {"error": str(e), "success": False}


@mcp.tool()
async def delete_task(
    task_id: str,
    authorization: str,
) -> dict[str, Any]:
    """Delete a task (soft delete).

    Args:
        task_id: ID of the task to delete
        authorization: Bearer token for authentication (required)

    Returns:
        Dictionary with success status, task data, and message
    """
    pool = await get_pool()

    # Authenticate and get user_id
    try:
        user_id = await extract_user_id_from_authorization(authorization, pool)
    except ValueError as e:
        return {"success": False, "error": f"Authentication failed: {str(e)}"}

    async with pool.acquire() as conn:
        async with conn.transaction():
            try:
                task = await conn.fetchrow(
                    "SELECT * FROM tasks WHERE id = $1 AND user_id = $2 AND deleted_at IS NULL",
                    task_id, user_id
                )

                if not task:
                    return {"error": f"Task with ID '{task_id}' not found", "success": False}

                now = datetime.now(timezone.utc)

                await conn.execute(
                    "UPDATE tasks SET deleted_at = $1 WHERE id = $2",
                    now, task_id
                )

                return {
                    "success": True,
                    "task": {"id": task_id, "title": task["title"], "status": "deleted"},
                    "message": f"🗑️ Task '{task['title']}' deleted",
                }
            except Exception as e:
                return {"error": str(e), "success": False}


@mcp.tool()
async def update_task(
    task_id: str,
    authorization: str,
    title: str | None = None,
    description: str | None = None,
    priority: str | None = None,
    due_date: str | None = None,
) -> dict[str, Any]:
    """Update an existing task.

    Args:
        task_id: ID of the task to update
        authorization: Bearer token for authentication (required)
        title: New title (optional)
        description: New description (optional)
        priority: New priority (optional)
        due_date: New due date (optional)

    Returns:
        Dictionary with success status, task data, and message
    """
    pool = await get_pool()

    # Authenticate and get user_id
    try:
        user_id = await extract_user_id_from_authorization(authorization, pool)
    except ValueError as e:
        return {"success": False, "error": f"Authentication failed: {str(e)}"}

    async with pool.acquire() as conn:
        try:
            task = await conn.fetchrow(
                "SELECT * FROM tasks WHERE id = $1 AND user_id = $2 AND deleted_at IS NULL",
                task_id, user_id
            )

            if not task:
                return {"error": f"Task with ID '{task_id}' not found", "success": False}

            updates = {}
            if title is not None:
                if not title.strip():
                    return {"error": "Title cannot be empty", "success": False}
                updates["title"] = title.strip()

            if description is not None:
                updates["description"] = description.strip() if description else None

            if priority is not None:
                priority_lower = priority.lower()
                if priority_lower not in ["low", "medium", "high"]:
                    return {
                        "error": f"Invalid priority '{priority}'. Must be 'low', 'medium', or 'high'.",
                        "success": False,
                    }
                updates["priority"] = priority_lower

            if due_date is not None:
                try:
                    # Parse the date with proper timezone handling
                    parsed_due_date = parser.parse(due_date)

                    # If the parsed date is naive (no timezone), assume UTC
                    if parsed_due_date.tzinfo is None:
                        parsed_due_date = parsed_due_date.replace(tzinfo=timezone.utc)
                    else:
                        # Convert to UTC if it has a different timezone
                        parsed_due_date = parsed_due_date.astimezone(timezone.utc)

                    updates["due_date"] = parsed_due_date
                except Exception as e:
                    return {"error": f"Invalid date format '{due_date}': {str(e)}", "success": False}

            if not updates:
                return {"error": "No valid updates provided", "success": False}

            now = datetime.now(timezone.utc)

            # Build update query
            set_clauses = [f"{k} = ${i+2}" for i, k in enumerate(updates.keys())]
            set_clauses.append(f"updated_at = ${len(set_clauses)+2}")

            await conn.execute(
                f"UPDATE tasks SET {', '.join(set_clauses)} WHERE id = $1",
                task_id, *updates.values(), now
            )

            return {
                "success": True,
                "task": {
                    "id": task_id,
                    "title": updates.get("title", task["title"]),
                    "description": updates.get("description", task["description"]),
                    "status": task["status"],
                    "priority": updates.get("priority", task["priority"]),
                    "due_date": updates.get("due_date", task["due_date"]).isoformat() if updates.get("due_date") else None,
                },
                "message": f"✏️ Task '{updates.get('title', task['title'])}' updated",
            }
        except Exception as e:
            return {"error": str(e), "success": False}


# Health check endpoint
@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "service": "mcp-task-server"}


# Root endpoint to provide info
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "MCP Task Management Server",
        "status": "running",
        "mcp_endpoint": "/mcp"
    }


# Configure allowed hosts for TransportSecurityMiddleware
# In production, set ALLOWED_HOSTS environment variable to comma-separated list of domains
# Example: ALLOWED_HOSTS="your-mcp-server.vercel.app,your-custom-domain.com"
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",")
if ALLOWED_HOSTS == [""]:
    # Development mode - allow localhost
    ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]
    print("⚠️  Running in development mode with unrestricted host access")
else:
    print(f"✅ Allowed hosts configured: {', '.join(ALLOWED_HOSTS)}")

# Mount MCP at /mcp
# Use streamable_http_app() method (correct API for FastMCP)
mcp_app = mcp.streamable_http_app()

app.mount("/mcp", mcp_app)
