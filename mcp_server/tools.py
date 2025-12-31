"""Standalone MCP tools - no dependency on backend/src structure.

These tools connect directly to the database using asyncpg.
"""

import os
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Optional
from dateutil import parser
import asyncpg

# Database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set")


# Remove asyncpg scheme for asyncpg.connect
def get_db_url() -> str:
    url = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
    return url.replace("+psycopg://", "postgresql://")


_pool: Optional[asyncpg.Pool] = None


async def get_pool() -> asyncpg.Pool:
    """Get or create connection pool."""
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(
            get_db_url(),
            min_size=1,
            max_size=5,
            command_timeout=60,
            max_inactive_connection_lifetime=60,
        )
    return _pool


async def close_pool():
    """Close the connection pool."""
    global _pool
    if _pool:
        await _pool.close()
        _pool = None


async def add_task(
    title: str,
    description: str | None = None,
    due_date: str | None = None,
    priority: str = "medium",
    tags: list[str] | None = None,
    user_id: str = "default_user",
) -> dict[str, Any]:
    """Add a new task to the user's task list."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            try:
                # Parse due date
                parsed_due_date = None
                if due_date:
                    # Simple date parsing
                    from dateutil import parser
                    try:
                        parsed_due_date = parser.parse(due_date)
                    except:
                        return {"error": f"Invalid date format: {due_date}", "success": False}

                # Validate priority
                priority_lower = priority.lower()
                if priority_lower not in ["low", "medium", "high"]:
                    return {
                        "error": f"Invalid priority '{priority}'. Must be 'low', 'medium', or 'high'.",
                        "success": False,
                    }

                # Create task
                task_id = f"task_{uuid.uuid4().hex[:12]}"
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
                        # Get or create tag
                        tag_id = f"tag_{uuid.uuid4().hex[:8]}"
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


async def list_tasks(
    status: str | None = None,
    priority: str | None = None,
    tags: list[str] | None = None,
    user_id: str = "default_user",
) -> dict[str, Any]:
    """List tasks with optional filters."""
    pool = await get_pool()
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


async def complete_task(
    task_id: str,
    user_id: str = "default_user",
) -> dict[str, Any]:
    """Mark a task as complete."""
    pool = await get_pool()
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


async def delete_task(
    task_id: str,
    user_id: str = "default_user",
) -> dict[str, Any]:
    """Delete a task (soft delete)."""
    pool = await get_pool()
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


async def update_task(
    task_id: str,
    title: str | None = None,
    description: str | None = None,
    priority: str | None = None,
    due_date: str | None = None,
    user_id: str = "default_user",
) -> dict[str, Any]:
    """Update an existing task."""
    pool = await get_pool()
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
                from dateutil import parser
                try:
                    updates["due_date"] = parser.parse(due_date)
                except:
                    return {"error": f"Invalid date format: {due_date}", "success": False}

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
            await conn.commit()

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
            await conn.rollback()
            return {"error": str(e), "success": False}
