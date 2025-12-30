"""MCP tools for task management operations.

These tools expose task operations to AI agents through the Model Context Protocol.
Each tool is registered with the FastMCP server using the @mcp.tool() decorator.
"""

from typing import Any

from mcp.server.fastmcp import Context

from src.core.logging import get_logger, log_tool_invocation
from src.mcp_server.mcp_instance import mcp
from src.mcp_server.database import get_session
from src.models.task import TaskCreate, TaskPriority, TaskStatus
from src.models.tag import TagCreate
from src.services.date_parser_service import DateParserService
from src.services.task_service import TaskService
from src.services.tag_service import TagService

logger = get_logger(__name__)


@mcp.tool()
async def add_task(
    title: str,
    description: str | None = None,
    due_date: str | None = None,
    priority: str = "medium",
    tags: list[str] | None = None,
    user_id: str = "default_user",  # Required - agent must pass actual user_id
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Add a new task to the user's task list.

    This tool allows the AI agent to create tasks based on natural language input.
    It handles date parsing, priority validation, and tag management automatically.

    Args:
        title: Task title (1-100 characters, required).
        description: Optional task description (max 500 characters).
        due_date: Optional due date in natural language (e.g., "tomorrow", "next Friday", "Dec 25").
        priority: Task priority level - "low", "medium", or "high" (default: "medium").
        tags: Optional list of tag names to apply to the task.
        user_id: User ID for task ownership - CRITICAL: Must be passed from the agent context.
        ctx: FastMCP context (automatically injected).

    Returns:
        Dictionary with task details including id, title, description, due_date, priority, and tags.

    Examples:
        - "Add a task to buy groceries tomorrow"
        - "Create a high priority task to finish the report by Friday with tags work, urgent"
        - "Add task: Call mom tonight at 7pm (tag: personal)"
    """
    try:
        logger.info(f"🔧 MCP add_task called: title='{title}', user_id='{user_id}'")
        logger.info(f"   Full args: title={title}, user_id={user_id}, priority={priority}, due_date={due_date}, tags={tags}")

        if ctx:
            await ctx.info(f"Creating task: {title}")

        # Create database session for this request
        async with get_session() as session:
            # Parse due date if provided
            parsed_due_date = None
            if due_date:
                date_parser = DateParserService()
                is_valid, error_msg = date_parser.validate_date(due_date)
                if not is_valid:
                    return {"error": error_msg, "success": False}
                parsed_due_date = date_parser.parse_date(due_date)

            # Validate and map priority
            priority_lower = priority.lower()
            if priority_lower not in ["low", "medium", "high"]:
                return {
                    "error": f"Invalid priority '{priority}'. Must be 'low', 'medium', or 'high'.",
                    "success": False,
                }
            priority_enum = TaskPriority[priority_lower.upper()]

            # Create task
            task_data = TaskCreate(
                title=title,
                description=description,
                priority=priority_enum,
                due_date=parsed_due_date,
            )

            task_service = TaskService(session)
            task = await task_service.create_task(task_data, user_id)

            # Add tags if provided
            task_tags = []
            if tags:
                tag_service = TagService(session)
                for tag_name in tags:
                    # Get or create tag
                    existing_tags = await tag_service.get_tags(user_id)
                    existing_tag = next(
                        (t for t in existing_tags if t.name.lower() == tag_name.lower()),
                        None,
                    )

                    if not existing_tag:
                        tag_create = TagCreate(name=tag_name, color="#3B82F6")
                        existing_tag = await tag_service.create_tag(tag_create, user_id)

                    # Add tag to task
                    await task_service.add_tag_to_task(task.id, existing_tag.id, user_id)
                    task_tags.append(tag_name)

            # Commit transaction
            await session.commit()

            # Refresh task to get tags
            await session.refresh(task)

            # Handle status and priority which might be enums or strings
            task_status = task.status.value if hasattr(task.status, 'value') else str(task.status)
            task_priority = task.priority.value if hasattr(task.priority, 'value') else str(task.priority)

            result = {
                "success": True,
                "task": {
                    "id": str(task.id),
                    "title": task.title,
                    "description": task.description,
                    "status": task_status,
                    "priority": task_priority,
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "created_at": task.created_at.isoformat(),
                    "tags": task_tags,
                },
                "message": f"✅ Task '{title}' created successfully",
            }

            if ctx:
                await ctx.info(f"Task created: {task.id}")
            log_tool_invocation(
                tool_name="add_task",
                args={"title": title, "due_date": due_date, "priority": priority, "tags": tags},
                result=result,
            )

            return result

    except Exception as e:
        logger.error(f"Error in add_task: {e}", exc_info=True)
        if ctx:
            await ctx.error(f"Failed to create task: {str(e)}")
        log_tool_invocation(
            tool_name="add_task",
            args={"title": title, "due_date": due_date, "priority": priority, "tags": tags},
            error=e,
        )
        return {"error": str(e), "success": False}


@mcp.tool()
async def list_tasks(
    status: str | None = None,
    priority: str | None = None,
    tags: list[str] | None = None,
    user_id: str = "default_user",  # TODO: Get from authentication
    ctx: Context | None = None,
) -> dict[str, Any]:
    """List tasks with optional filters.

    This tool allows the AI agent to query the user's tasks with various filters.
    Returns a list of tasks matching the specified criteria.

    Args:
        status: Filter by status - "pending" or "completed" (optional).
        priority: Filter by priority - "low", "medium", or "high" (optional).
        tags: Filter by tag names - returns tasks with ANY of these tags (optional).
        user_id: User ID for filtering tasks (default: "default_user").
        ctx: FastMCP context (automatically injected).

    Returns:
        Dictionary with "tasks" list and "count" of matching tasks.

    Examples:
        - "Show me all my tasks"
        - "What are my pending tasks?"
        - "List high priority tasks"
        - "Show tasks tagged with work"
    """
    try:
        if ctx:
            await ctx.info(f"Listing tasks with filters: status={status}, priority={priority}, tags={tags}")

        # Create database session for this request
        async with get_session() as session:
            # Validate status
            status_enum = None
            if status:
                status_lower = status.lower()
                if status_lower not in ["pending", "completed"]:
                    return {
                        "error": f"Invalid status '{status}'. Must be 'pending' or 'completed'.",
                        "success": False,
                    }
                status_enum = TaskStatus[status_lower.upper()]

            # Validate priority
            priority_enum = None
            if priority:
                priority_lower = priority.lower()
                if priority_lower not in ["low", "medium", "high"]:
                    return {
                        "error": f"Invalid priority '{priority}'. Must be 'low', 'medium', or 'high'.",
                        "success": False,
                    }
                priority_enum = TaskPriority[priority_lower.upper()]

            # Get tasks from service using the proper API with filters
            task_service = TaskService(session)
            task_list_response = await task_service.get_tasks(
                user_id=user_id,
                status=status_enum,
                priority=priority_enum,
                limit=100,  # Get up to 100 tasks
            )

            # Build task list from response
            filtered_tasks = []
            for task_response in task_list_response.tasks:
                # Apply tag filter if needed (service doesn't filter by tag name)
                if tags:
                    task_tag_names = [tag.lower() for tag in task_response.tags]
                    if not any(tag.lower() in task_tag_names for tag in tags):
                        continue

                filtered_tasks.append(
                    {
                        "id": str(task_response.id),
                        "title": task_response.title,
                        "description": task_response.description,
                        "status": task_response.status,
                        "priority": task_response.priority,
                        "due_date": task_response.due_date.isoformat() if task_response.due_date else None,
                        "created_at": task_response.created_at.isoformat(),
                        "completed_at": (
                            task_response.completed_at.isoformat() if task_response.completed_at else None
                        ),
                        "tags": task_response.tags,
                    }
                )

            result = {
                "success": True,
                "tasks": filtered_tasks,
                "count": len(filtered_tasks),
                "message": f"Found {len(filtered_tasks)} task(s)",
            }

            if ctx:
                await ctx.info(f"Found {len(filtered_tasks)} tasks")
            log_tool_invocation(
                tool_name="list_tasks",
                args={"status": status, "priority": priority, "tags": tags},
                result={"count": result["count"]},
            )

            return result

    except Exception as e:
        logger.error(f"Error in list_tasks: {e}", exc_info=True)
        if ctx:
            await ctx.error(f"Failed to list tasks: {str(e)}")
        log_tool_invocation(
            tool_name="list_tasks",
            args={"status": status, "priority": priority, "tags": tags},
            error=e,
        )
        return {"error": str(e), "success": False}


@mcp.tool()
async def complete_task(
    task_id: str,
    user_id: str = "default_user",
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Mark a task as complete.

    Args:
        task_id: The ID of the task to complete.
        user_id: User ID for task ownership (default: "default_user").
        ctx: FastMCP context (automatically injected).

    Returns:
        Dictionary with task details and completion confirmation.

    Examples:
        - "Mark task 5 as complete"
        - "I'm done with the grocery task"
    """
    try:
        if ctx:
            await ctx.info(f"Completing task: {task_id}")

        async with get_session() as session:
            task_service = TaskService(session)

            task = await task_service.get_task(task_id, user_id)

            if not task:
                return {
                    "error": f"Task with ID '{task_id}' not found",
                    "success": False,
                }

            if task.status == TaskStatus.COMPLETED:
                return {
                    "error": f"Task '{task.title}' is already completed",
                    "success": False,
                }

            if task.deleted_at:
                return {
                    "error": f"Task '{task.title}' has been deleted",
                    "success": False,
                }

            completed_task = await task_service.complete_task(task_id, user_id)
            await session.commit()

            # Handle status which might be enum or string
            completed_status = completed_task.status.value if hasattr(completed_task.status, 'value') else str(completed_task.status)

            result = {
                "success": True,
                "task": {
                    "id": str(completed_task.id),
                    "title": completed_task.title,
                    "status": completed_status,
                    "completed_at": (
                        completed_task.completed_at.isoformat()
                        if completed_task.completed_at
                        else None
                    ),
                },
                "message": f"✅ Task '{completed_task.title}' marked as complete",
            }

            if ctx:
                await ctx.info(f"Task completed: {completed_task.id}")

            return result

    except Exception as e:
        logger.error(f"Error in complete_task: {e}", exc_info=True)
        return {"error": str(e), "success": False}


@mcp.tool()
async def delete_task(
    task_id: str,
    user_id: str = "default_user",
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Delete a task from the list (soft delete).

    Args:
        task_id: The ID of the task to delete.
        user_id: User ID for task ownership (default: "default_user").
        ctx: FastMCP context (automatically injected).

    Returns:
        Dictionary with task details and deletion confirmation.
    """
    try:
        if ctx:
            await ctx.info(f"Deleting task: {task_id}")

        async with get_session() as session:
            task_service = TaskService(session)

            task = await task_service.get_task(task_id, user_id)

            if not task:
                return {
                    "error": f"Task with ID '{task_id}' not found",
                    "success": False,
                }

            if task.deleted_at:
                return {
                    "error": f"Task '{task.title}' has already been deleted",
                    "success": False,
                }

            task_title = task.title
            deleted_task = await task_service.delete_task(task_id, user_id)
            await session.commit()

            result = {
                "success": True,
                "task": {
                    "id": str(deleted_task.id),
                    "title": task_title,
                    "status": "deleted",
                },
                "message": f"🗑️ Task '{task_title}' deleted",
            }

            if ctx:
                await ctx.info(f"Task deleted: {task_id}")

            return result

    except Exception as e:
        logger.error(f"Error in delete_task: {e}", exc_info=True)
        return {"error": str(e), "success": False}


@mcp.tool()
async def update_task(
    task_id: str,
    title: str | None = None,
    description: str | None = None,
    priority: str | None = None,
    due_date: str | None = None,
    user_id: str = "default_user",
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Update an existing task.

    Args:
        task_id: The ID of the task to update.
        title: New task title (optional).
        description: New task description (optional).
        priority: New priority level - "low", "medium", or "high" (optional).
        due_date: New due date in natural language (optional).
        user_id: User ID for task ownership (default: "default_user").
        ctx: FastMCP context (automatically injected).

    Returns:
        Dictionary with updated task details.
    """
    try:
        if ctx:
            await ctx.info(f"Updating task: {task_id}")

        async with get_session() as session:
            task_service = TaskService(session)

            task = await task_service.get_task(task_id, user_id)

            if not task:
                return {
                    "error": f"Task with ID '{task_id}' not found",
                    "success": False,
                }

            if task.deleted_at:
                return {
                    "error": f"Task '{task.title}' has been deleted",
                    "success": False,
                }

            updates: dict[str, Any] = {}

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
                updates["priority"] = TaskPriority[priority_lower.upper()]

            if due_date is not None:
                date_parser = DateParserService()
                is_valid, error_msg = date_parser.validate_date(due_date)
                if not is_valid:
                    return {"error": error_msg, "success": False}
                updates["due_date"] = date_parser.parse_date(due_date)

            if not updates:
                return {"error": "No valid updates provided", "success": False}

            # Call service with individual parameters
            updated_task = await task_service.update_task(
                task_id=task_id,
                user_id=user_id,
                title=updates.get("title"),
                description=updates.get("description"),
                due_date=updates.get("due_date"),
                priority=updates.get("priority"),
            )
            await session.commit()
            await session.refresh(updated_task)

            # Handle status and priority which might be enums or strings
            updated_status = updated_task.status.value if hasattr(updated_task.status, 'value') else str(updated_task.status)
            updated_priority = updated_task.priority.value if hasattr(updated_task.priority, 'value') else str(updated_task.priority)

            result = {
                "success": True,
                "task": {
                    "id": str(updated_task.id),
                    "title": updated_task.title,
                    "description": updated_task.description,
                    "status": updated_status,
                    "priority": updated_priority,
                    "due_date": (
                        updated_task.due_date.isoformat()
                        if updated_task.due_date
                        else None
                    ),
                },
                "message": f"✏️ Task '{updated_task.title}' updated",
            }

            if ctx:
                await ctx.info(f"Task updated: {updated_task.id}")

            return result

    except Exception as e:
        logger.error(f"Error in update_task: {e}", exc_info=True)
        return {"error": str(e), "success": False}
