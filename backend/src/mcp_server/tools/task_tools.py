"""MCP tools for task management operations.

These tools expose task operations to AI agents through the Model Context Protocol.
Each tool is registered with the FastMCP server using the @mcp.tool() decorator.
"""

from typing import Any

from mcp.shared.context import Context
from mcp.server.fastmcp.utilities import CurrentContext

from src.core.logging import get_logger, log_tool_invocation
from src.mcp_server.server import mcp, db
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
    user_id: str = "default_user",  # TODO: Get from authentication
    ctx: Context = CurrentContext(),
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
        user_id: User ID for task ownership (default: "default_user").
        ctx: FastMCP context (automatically injected).

    Returns:
        Dictionary with task details including id, title, description, due_date, priority, and tags.

    Examples:
        - "Add a task to buy groceries tomorrow"
        - "Create a high priority task to finish the report by Friday with tags work, urgent"
        - "Add task: Call mom tonight at 7pm (tag: personal)"
    """
    try:
        await ctx.info(f"Creating task: {title}")

        # Create database session for this request
        async with db.get_session() as session:
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

            result = {
                "success": True,
                "task": {
                    "id": str(task.id),
                    "title": task.title,
                    "description": task.description,
                    "status": task.status.value,
                    "priority": task.priority.value,
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "created_at": task.created_at.isoformat(),
                    "tags": task_tags,
                },
                "message": f"✅ Task '{title}' created successfully",
            }

            await ctx.info(f"Task created: {task.id}")
            log_tool_invocation(
                tool_name="add_task",
                args={"title": title, "due_date": due_date, "priority": priority, "tags": tags},
                result=result,
            )

            return result

    except Exception as e:
        logger.error(f"Error in add_task: {e}", exc_info=True)
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
    ctx: Context = CurrentContext(),
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
        await ctx.info(f"Listing tasks with filters: status={status}, priority={priority}, tags={tags}")

        # Create database session for this request
        async with db.get_session() as session:
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

            # Get tasks from service
            task_service = TaskService(session)
            all_tasks = await task_service.get_tasks(user_id)

            # Apply filters
            filtered_tasks = []
            for task in all_tasks:
                # Skip deleted tasks
                if task.deleted_at:
                    continue

                # Apply status filter
                if status_enum and task.status != status_enum:
                    continue

                # Apply priority filter
                if priority_enum and task.priority != priority_enum:
                    continue

                # Apply tag filter
                if tags:
                    task_tag_names = [
                        tt.tag.name.lower()
                        for tt in task.task_tags
                        if hasattr(tt, "tag") and tt.tag
                    ]
                    if not any(tag.lower() in task_tag_names for tag in tags):
                        continue

                # Build task dict
                task_tags_list = []
                if hasattr(task, "task_tags") and task.task_tags:
                    task_tags_list = [
                        tt.tag.name for tt in task.task_tags if hasattr(tt, "tag") and tt.tag
                    ]

                filtered_tasks.append(
                    {
                        "id": str(task.id),
                        "title": task.title,
                        "description": task.description,
                        "status": task.status.value,
                        "priority": task.priority.value,
                        "due_date": task.due_date.isoformat() if task.due_date else None,
                        "created_at": task.created_at.isoformat(),
                        "completed_at": (
                            task.completed_at.isoformat() if task.completed_at else None
                        ),
                        "tags": task_tags_list,
                    }
                )

            result = {
                "success": True,
                "tasks": filtered_tasks,
                "count": len(filtered_tasks),
                "message": f"Found {len(filtered_tasks)} task(s)",
            }

            await ctx.info(f"Found {len(filtered_tasks)} tasks")
            log_tool_invocation(
                tool_name="list_tasks",
                args={"status": status, "priority": priority, "tags": tags},
                result={"count": result["count"]},
            )

            return result

    except Exception as e:
        logger.error(f"Error in list_tasks: {e}", exc_info=True)
        await ctx.error(f"Failed to list tasks: {str(e)}")
        log_tool_invocation(
            tool_name="list_tasks",
            args={"status": status, "priority": priority, "tags": tags},
            error=e,
        )
        return {"error": str(e), "success": False}
