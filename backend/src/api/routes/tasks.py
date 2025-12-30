"""API routes for task operations."""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import get_current_user
from src.db.session import get_db
from src.models.task import TaskCreate, TaskResponse, TaskStatus
from src.models.user import User
from src.schemas.responses import StandardizedResponse
from src.schemas.task_schemas import (
    TaskListResponse,
    TaskUpdateRequest,
    BulkToggleRequest,
    BulkDeleteRequest,
    BulkOperationResponse,
    DueDateStatsResponse,
    UpdateDueDateRequest,
    AnalyticsStatsResponse,
    CompletionTrendResponse,
    PriorityBreakdownResponse,
    ReorderTasksRequest,
)
from src.services.task_service import TaskService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=StandardizedResponse[TaskResponse],
)
async def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> StandardizedResponse[TaskResponse]:
    """Create a new task for the authenticated user.

    Args:
        task_data: Task creation data (title, description, priority).
        current_user: Authenticated user from JWT token.
        session: Database session.

    Returns:
        StandardizedResponse containing the created task.

    Raises:
        HTTPException: 400 for validation errors, 401 for auth errors, 500 for server errors.
    """
    try:
        # Initialize service
        service = TaskService(session)

        # Create task (user_id is extracted from JWT token)
        task = await service.create_task(task_data, current_user.id)

        # Log successful creation
        logger.info(f"Task created: id={task.id}, user_id={current_user.id}, title={task.title[:50]}")

        # Return success response
        return StandardizedResponse(
            success=True,
            message="Task created successfully",
            data=TaskResponse.model_validate(task),
        )

    except ValidationError as e:
        # Handle Pydantic validation errors
        logger.warning(f"Validation error creating task: {e}")
        errors = []
        for err in e.errors():
            errors.append({
                "field": ".".join(str(loc) for loc in err["loc"]),
                "message": err["msg"],
            })

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Invalid input data",
                },
                "details": errors,
            },
        )

    except ValueError as e:
        # Handle value errors (from validators)
        logger.warning(f"Value error creating task: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": str(e),
                },
            },
        )

    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Failed to create task: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Failed to create task. Please try again later.",
                },
            },
        )


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=StandardizedResponse[TaskListResponse],
)
async def get_tasks(
    page: int = 1,
    limit: int = 20,
    status_filter: TaskStatus | None = None,
    priority: str | None = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    search: str | None = None,
    due_date_from: str | None = None,
    due_date_to: str | None = None,
    has_due_date: bool | None = None,
    tags: str | None = None,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> StandardizedResponse[TaskListResponse]:
    """Get paginated list of tasks with filtering and sorting.

    Args:
        page: Page number (1-indexed, default: 1).
        limit: Items per page (default: 20, max: 100).
        status_filter: Filter by task status (optional).
        priority: Filter by task priority: low, medium, or high (optional).
        sort_by: Field to sort by (default: "created_at").
        sort_order: Sort direction "asc" or "desc" (default: "desc").
        search: Search in task title and description (optional).
        due_date_from: Filter tasks due after this date (ISO 8601, optional).
        due_date_to: Filter tasks due before this date (ISO 8601, optional).
        has_due_date: Filter tasks with/without due dates (optional).
        tags: Comma-separated list of tag IDs to filter by (optional).
        current_user: Authenticated user from JWT token.
        session: Database session.

    Returns:
        StandardizedResponse containing task list with metadata and pagination.

    Raises:
        HTTPException: 400 for validation errors, 401 for auth errors, 500 for server errors.
    """
    try:
        # Initialize service
        service = TaskService(session)

        # Parse priority string to enum if provided
        priority_filter = None
        if priority:
            try:
                from src.models.task import TaskPriority

                priority_filter = TaskPriority(priority.lower())
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "success": False,
                        "error": {
                            "code": "VALIDATION_ERROR",
                            "message": f"Invalid priority: {priority}. Must be low, medium, or high",
                        },
                    },
                )

        # Parse due date strings to datetime if provided
        from datetime import datetime

        due_date_from_dt = None
        due_date_to_dt = None

        if due_date_from:
            try:
                due_date_from_dt = datetime.fromisoformat(due_date_from.replace("Z", "+00:00"))
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "success": False,
                        "error": {
                            "code": "VALIDATION_ERROR",
                            "message": f"Invalid due_date_from format: {due_date_from}",
                        },
                    },
                )

        if due_date_to:
            try:
                due_date_to_dt = datetime.fromisoformat(due_date_to.replace("Z", "+00:00"))
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "success": False,
                        "error": {
                            "code": "VALIDATION_ERROR",
                            "message": f"Invalid due_date_to format: {due_date_to}",
                        },
                    },
                )

        # Parse tag IDs if provided
        tag_ids = None
        if tags:
            tag_ids = [tag_id.strip() for tag_id in tags.split(",") if tag_id.strip()]

        # Get tasks with filtering and pagination
        task_list = await service.get_tasks(
            user_id=current_user.id,
            page=page,
            limit=limit,
            status=status_filter,
            priority=priority_filter,
            sort_by=sort_by,
            sort_order=sort_order,
            search=search,
            due_date_from=due_date_from_dt,
            due_date_to=due_date_to_dt,
            has_due_date=has_due_date,
            tag_ids=tag_ids,
        )

        # Log successful retrieval
        logger.info(
            f"Tasks retrieved: user_id={current_user.id}, page={page}, "
            f"total_items={task_list.pagination.total_items}"
        )

        # Return success response
        return StandardizedResponse(
            success=True,
            message="Tasks retrieved successfully",
            data=task_list,
        )

    except ValueError as e:
        # Handle validation errors (invalid page/limit)
        logger.warning(f"Validation error retrieving tasks: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": str(e),
                },
            },
        )

    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Failed to retrieve tasks: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Failed to retrieve tasks. Please try again later.",
                },
            },
        )


@router.put(
    "/{task_id}",
    status_code=status.HTTP_200_OK,
    response_model=StandardizedResponse[TaskResponse],
)
async def update_task(
    task_id: str,
    update_data: TaskUpdateRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> StandardizedResponse[TaskResponse]:
    """Update a task's fields.

    Args:
        task_id: UUID of the task to update.
        update_data: Task update data (title, description, due_date, notes, manual_order).
        current_user: Authenticated user from JWT token.
        session: Database session.

    Returns:
        StandardizedResponse containing the updated task.

    Raises:
        HTTPException: 400 for validation errors, 403 for permission errors, 404 for not found, 500 for server errors.
    """
    try:
        # Initialize service
        service = TaskService(session)

        # Update task
        task = await service.update_task(
            task_id=task_id,
            user_id=current_user.id,
            title=update_data.title,
            description=update_data.description,
            due_date=update_data.due_date,
            notes=update_data.notes,
            manual_order=update_data.manual_order,
        )

        # Log successful update
        logger.info(
            f"Task updated: id={task.id}, user_id={current_user.id}, "
            f"title_changed={update_data.title is not None}, "
            f"description_changed={update_data.description is not None}"
        )

        # Return success response
        return StandardizedResponse(
            success=True,
            message="Task updated successfully",
            data=TaskResponse.model_validate(task),
        )

    except PermissionError as e:
        # Handle permission errors
        logger.warning(f"Permission denied updating task {task_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "success": False,
                "error": {
                    "code": "PERMISSION_DENIED",
                    "message": str(e),
                },
            },
        )

    except ValueError as e:
        # Handle validation errors (no changes, task not found, etc.)
        error_message = str(e)
        logger.warning(f"Validation error updating task {task_id}: {error_message}")

        # Determine if it's a not found error
        if "not found" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "success": False,
                    "error": {
                        "code": "NOT_FOUND",
                        "message": error_message,
                    },
                },
            )

        # Otherwise it's a validation error
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": error_message,
                },
            },
        )

    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Failed to update task {task_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Failed to update task. Please try again later.",
                },
            },
        )


@router.patch(
    "/{task_id}/toggle",
    status_code=status.HTTP_200_OK,
    response_model=StandardizedResponse[TaskResponse],
)
async def toggle_task_status(
    task_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> StandardizedResponse[TaskResponse]:
    """Toggle a task's status between pending and completed.

    Args:
        task_id: UUID of the task to toggle.
        current_user: Authenticated user from JWT token.
        session: Database session.

    Returns:
        StandardizedResponse containing the updated task.

    Raises:
        HTTPException: 403 for permission errors, 404 for not found, 500 for server errors.
    """
    try:
        # Initialize service
        service = TaskService(session)

        # Toggle task status
        task = await service.toggle_task_status(task_id=task_id, user_id=current_user.id)

        # Log successful toggle
        logger.info(
            f"Task status toggled: id={task.id}, user_id={current_user.id}, new_status={task.status}"
        )

        # Return success response
        return StandardizedResponse(
            success=True,
            message=f"Task status updated to {task.status}",
            data=TaskResponse.model_validate(task),
        )

    except PermissionError as e:
        logger.warning(f"Permission denied toggling task {task_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "success": False,
                "error": {"code": "PERMISSION_DENIED", "message": str(e)},
            },
        )

    except ValueError as e:
        error_message = str(e)
        logger.warning(f"Validation error toggling task {task_id}: {error_message}")

        if "not found" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "success": False,
                    "error": {"code": "NOT_FOUND", "message": error_message},
                },
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "error": {"code": "VALIDATION_ERROR", "message": error_message},
            },
        )

    except Exception as e:
        logger.error(f"Failed to toggle task {task_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Failed to toggle task status. Please try again later.",
                },
            },
        )


@router.post(
    "/bulk-toggle",
    status_code=status.HTTP_200_OK,
    response_model=StandardizedResponse[BulkOperationResponse],
)
async def bulk_toggle_tasks(
    request: BulkToggleRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> StandardizedResponse[BulkOperationResponse]:
    """Toggle multiple tasks to a target status.

    Args:
        request: Bulk toggle request with task IDs and target status.
        current_user: Authenticated user from JWT token.
        session: Database session.

    Returns:
        StandardizedResponse with updated task count and task list.

    Raises:
        HTTPException: 400 for validation errors, 403 for permission errors, 500 for server errors.
    """
    try:
        # Initialize service
        service = TaskService(session)

        # Convert UUIDs to strings
        task_ids = [str(task_id) for task_id in request.task_ids]

        # Bulk toggle
        tasks = await service.bulk_toggle_status(
            task_ids=task_ids,
            target_status=request.target_status,
            user_id=current_user.id,
        )

        # Log successful bulk operation
        logger.info(
            f"Bulk toggle completed: user_id={current_user.id}, "
            f"count={len(tasks)}, target_status={request.target_status}"
        )

        # Return success response
        return StandardizedResponse(
            success=True,
            message=f"Successfully updated {len(tasks)} tasks to {request.target_status}",
            data=BulkOperationResponse(
                updated_count=len(tasks),
                tasks=[TaskResponse.model_validate(task) for task in tasks],
            ),
        )

    except PermissionError as e:
        logger.warning(f"Permission denied in bulk toggle: {e}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "success": False,
                "error": {"code": "PERMISSION_DENIED", "message": str(e)},
            },
        )

    except ValueError as e:
        error_message = str(e)
        logger.warning(f"Validation error in bulk toggle: {error_message}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "error": {"code": "VALIDATION_ERROR", "message": error_message},
            },
        )

    except Exception as e:
        logger.error(f"Failed bulk toggle: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Failed to toggle tasks. Please try again later.",
                },
            },
        )


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_200_OK,
    response_model=StandardizedResponse[TaskResponse],
)
async def delete_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> StandardizedResponse[TaskResponse]:
    """Soft delete a task by setting deleted_at timestamp.

    Args:
        task_id: UUID of the task to delete.
        current_user: Authenticated user from JWT token.
        session: Database session.

    Returns:
        StandardizedResponse containing the soft-deleted task.

    Raises:
        HTTPException: 403 for permission errors, 404 for not found, 500 for server errors.
    """
    try:
        # Initialize service
        service = TaskService(session)

        # Soft delete task
        task = await service.soft_delete_task(task_id=task_id, user_id=current_user.id)

        # Log successful deletion
        logger.info(f"Task soft deleted: id={task.id}, user_id={current_user.id}")

        # Return success response
        return StandardizedResponse(
            success=True,
            message="Task moved to trash",
            data=TaskResponse.model_validate(task),
        )

    except PermissionError as e:
        logger.warning(f"Permission denied deleting task {task_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "success": False,
                "error": {"code": "PERMISSION_DENIED", "message": str(e)},
            },
        )

    except ValueError as e:
        error_message = str(e)
        logger.warning(f"Validation error deleting task {task_id}: {error_message}")

        if "not found" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "success": False,
                    "error": {"code": "NOT_FOUND", "message": error_message},
                },
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "error": {"code": "VALIDATION_ERROR", "message": error_message},
            },
        )

    except Exception as e:
        logger.error(f"Failed to delete task {task_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Failed to delete task. Please try again later.",
                },
            },
        )


@router.post(
    "/bulk-delete",
    status_code=status.HTTP_200_OK,
    response_model=StandardizedResponse[BulkOperationResponse],
)
async def bulk_delete_tasks(
    request: BulkDeleteRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> StandardizedResponse[BulkOperationResponse]:
    """Soft delete multiple tasks.

    Args:
        request: Request with task IDs to delete.
        current_user: Authenticated user from JWT token.
        session: Database session.

    Returns:
        StandardizedResponse with deleted task count and task list.

    Raises:
        HTTPException: 400 for validation errors, 403 for permission errors, 500 for server errors.
    """
    try:
        # Initialize service
        service = TaskService(session)

        # Convert UUIDs to strings
        task_ids = [str(task_id) for task_id in request.task_ids]

        # Bulk delete
        tasks = await service.bulk_delete_tasks(task_ids=task_ids, user_id=current_user.id)

        # Log successful bulk operation
        logger.info(f"Bulk delete completed: user_id={current_user.id}, count={len(tasks)}")

        # Return success response
        return StandardizedResponse(
            success=True,
            message=f"Successfully moved {len(tasks)} tasks to trash",
            data=BulkOperationResponse(
                updated_count=len(tasks),
                tasks=[TaskResponse.model_validate(task) for task in tasks],
            ),
        )

    except PermissionError as e:
        logger.warning(f"Permission denied in bulk delete: {e}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "success": False,
                "error": {"code": "PERMISSION_DENIED", "message": str(e)},
            },
        )

    except ValueError as e:
        error_message = str(e)
        logger.warning(f"Validation error in bulk delete: {error_message}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "error": {"code": "VALIDATION_ERROR", "message": error_message},
            },
        )

    except Exception as e:
        logger.error(f"Failed bulk delete: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Failed to delete tasks. Please try again later.",
                },
            },
        )


@router.patch(
    "/reorder",
    status_code=status.HTTP_200_OK,
    response_model=StandardizedResponse[BulkOperationResponse],
)
async def reorder_tasks(
    request: ReorderTasksRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> StandardizedResponse[BulkOperationResponse]:
    """Reorder tasks by updating their manual_order field.

    Args:
        request: Reorder request with ordered list of task IDs.
        current_user: Authenticated user from JWT token.
        session: Database session.

    Returns:
        StandardizedResponse with updated task count and task list.

    Raises:
        HTTPException: 400 for validation errors, 403 for permission errors, 500 for server errors.
    """
    try:
        # Initialize service
        service = TaskService(session)

        # Convert UUIDs to strings
        task_ids = [str(task_id) for task_id in request.task_ids]

        # Reorder tasks
        tasks = await service.reorder_tasks(task_ids=task_ids, user_id=current_user.id)

        # Log successful reorder operation
        logger.info(f"Reorder completed: user_id={current_user.id}, count={len(tasks)}")

        # Return success response
        return StandardizedResponse(
            success=True,
            message=f"Successfully reordered {len(tasks)} tasks",
            data=BulkOperationResponse(
                updated_count=len(tasks),
                tasks=[TaskResponse.model_validate(task) for task in tasks],
            ),
        )

    except PermissionError as e:
        logger.warning(f"Permission denied in reorder: {e}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "success": False,
                "error": {"code": "PERMISSION_DENIED", "message": str(e)},
            },
        )

    except ValueError as e:
        error_message = str(e)
        logger.warning(f"Validation error in reorder: {error_message}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "error": {"code": "VALIDATION_ERROR", "message": error_message},
            },
        )

    except Exception as e:
        logger.error(f"Failed reorder: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Failed to reorder tasks. Please try again later.",
                },
            },
        )


@router.get(
    "/trash",
    status_code=status.HTTP_200_OK,
    response_model=StandardizedResponse[TaskListResponse],
)
async def get_trash(
    page: int = 1,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> StandardizedResponse[TaskListResponse]:
    """Get paginated list of soft-deleted tasks (trash view).

    Args:
        page: Page number (1-indexed, default: 1).
        limit: Items per page (default: 20, max: 100).
        current_user: Authenticated user from JWT token.
        session: Database session.

    Returns:
        StandardizedResponse containing trash task list with metadata and pagination.

    Raises:
        HTTPException: 400 for validation errors, 401 for auth errors, 500 for server errors.
    """
    try:
        # Initialize service
        service = TaskService(session)

        # Get trash with pagination
        task_list = await service.get_trash(user_id=current_user.id, page=page, limit=limit)

        # Log successful retrieval
        logger.info(
            f"Trash retrieved: user_id={current_user.id}, page={page}, "
            f"total_items={task_list.pagination.total_items}"
        )

        # Return success response
        return StandardizedResponse(
            success=True,
            message="Trash retrieved successfully",
            data=task_list,
        )

    except ValueError as e:
        logger.warning(f"Validation error retrieving trash: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "error": {"code": "VALIDATION_ERROR", "message": str(e)},
            },
        )

    except Exception as e:
        logger.error(f"Failed to retrieve trash: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Failed to retrieve trash. Please try again later.",
                },
            },
        )


@router.post(
    "/{task_id}/restore",
    status_code=status.HTTP_200_OK,
    response_model=StandardizedResponse[TaskResponse],
)
async def restore_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> StandardizedResponse[TaskResponse]:
    """Restore a soft-deleted task from trash.

    Args:
        task_id: UUID of the task to restore.
        current_user: Authenticated user from JWT token.
        session: Database session.

    Returns:
        StandardizedResponse containing the restored task.

    Raises:
        HTTPException: 403 for permission errors, 404 for not found, 500 for server errors.
    """
    try:
        # Initialize service
        service = TaskService(session)

        # Restore task
        task = await service.restore_task(task_id=task_id, user_id=current_user.id)

        # Log successful restore
        logger.info(f"Task restored: id={task.id}, user_id={current_user.id}")

        # Return success response
        return StandardizedResponse(
            success=True,
            message="Task restored successfully",
            data=TaskResponse.model_validate(task),
        )

    except PermissionError as e:
        logger.warning(f"Permission denied restoring task {task_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "success": False,
                "error": {"code": "PERMISSION_DENIED", "message": str(e)},
            },
        )

    except ValueError as e:
        error_message = str(e)
        logger.warning(f"Validation error restoring task {task_id}: {error_message}")

        if "not found" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "success": False,
                    "error": {"code": "NOT_FOUND", "message": error_message},
                },
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "error": {"code": "VALIDATION_ERROR", "message": error_message},
            },
        )

    except Exception as e:
        logger.error(f"Failed to restore task {task_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Failed to restore task. Please try again later.",
                },
            },
        )


@router.delete(
    "/{task_id}/permanent",
    status_code=status.HTTP_200_OK,
    response_model=StandardizedResponse[dict],
)
async def permanent_delete_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> StandardizedResponse[dict]:
    """Permanently delete a task from the database (irreversible).

    Args:
        task_id: UUID of the task to permanently delete.
        current_user: Authenticated user from JWT token.
        session: Database session.

    Returns:
        StandardizedResponse with success message.

    Raises:
        HTTPException: 403 for permission errors, 404 for not found, 500 for server errors.
    """
    try:
        # Initialize service
        service = TaskService(session)

        # Permanent delete
        await service.permanent_delete(task_id=task_id, user_id=current_user.id)

        # Log successful permanent deletion
        logger.info(f"Task permanently deleted: id={task_id}, user_id={current_user.id}")

        # Return success response
        return StandardizedResponse(
            success=True,
            message="Task permanently deleted",
            data={"task_id": task_id},
        )

    except PermissionError as e:
        logger.warning(f"Permission denied permanently deleting task {task_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "success": False,
                "error": {"code": "PERMISSION_DENIED", "message": str(e)},
            },
        )

    except ValueError as e:
        error_message = str(e)
        logger.warning(f"Validation error permanently deleting task {task_id}: {error_message}")

        if "not found" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "success": False,
                    "error": {"code": "NOT_FOUND", "message": error_message},
                },
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "error": {"code": "VALIDATION_ERROR", "message": error_message},
            },
        )

    except Exception as e:
        logger.error(f"Failed to permanently delete task {task_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Failed to permanently delete task. Please try again later.",
                },
            },
        )


# ============================================================================
# Due Date Management Routes
# ============================================================================


@router.get(
    "/due",
    response_model=StandardizedResponse[TaskListResponse],
)
async def get_tasks_by_due_date(
    filter: str | None = None,
    page: int = 1,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> StandardizedResponse[TaskListResponse]:
    """Get tasks filtered by due date criteria.

    Args:
        filter: Due date filter (overdue/today/tomorrow/this_week/next_week/no_due_date).
        page: Page number (1-indexed).
        limit: Items per page (max 100).
        current_user: Authenticated user.
        session: Database session.

    Returns:
        StandardizedResponse containing filtered tasks list with pagination.
    """
    try:
        service = TaskService(session)

        # Get filtered tasks
        result = await service.get_tasks_by_due_date(
            user_id=current_user.id, filter=filter, page=page, limit=limit
        )

        logger.info(
            f"Retrieved due date filtered tasks: filter={filter}, "
            f"user_id={current_user.id}, count={len(result.tasks)}"
        )

        return StandardizedResponse(
            success=True, message="Tasks retrieved successfully", data=result
        )

    except ValueError as e:
        logger.warning(f"Invalid filter for due date tasks: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "error": {"code": "INVALID_FILTER", "message": str(e)},
            },
        )

    except Exception as e:
        logger.error(f"Failed to retrieve due date filtered tasks: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Failed to retrieve tasks. Please try again later.",
                },
            },
        )


@router.patch(
    "/{task_id}/due-date",
    response_model=StandardizedResponse[TaskResponse],
)
async def update_task_due_date(
    task_id: UUID,
    request: UpdateDueDateRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> StandardizedResponse[TaskResponse]:
    """Update or remove a task's due date.

    Args:
        task_id: UUID of the task to update.
        request: Due date update request (due_date or None to remove).
        current_user: Authenticated user.
        session: Database session.

    Returns:
        StandardizedResponse containing the updated task.

    Raises:
        HTTPException: 404 if task not found, 403 if permission denied.
    """
    try:
        service = TaskService(session)

        # Update due date
        task = await service.update_task_due_date(
            task_id=str(task_id), user_id=current_user.id, due_date=request.due_date
        )

        logger.info(f"Task due date updated: task_id={task_id}, due_date={request.due_date}")

        return StandardizedResponse(
            success=True,
            message="Task due date updated successfully",
            data=TaskResponse.model_validate(task),
        )

    except PermissionError as e:
        logger.warning(f"Permission denied updating due date for task {task_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "success": False,
                "error": {"code": "PERMISSION_DENIED", "message": str(e)},
            },
        )

    except ValueError as e:
        error_message = str(e)
        logger.warning(f"Validation error updating due date for task {task_id}: {error_message}")

        if "not found" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "success": False,
                    "error": {"code": "NOT_FOUND", "message": error_message},
                },
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "error": {"code": "VALIDATION_ERROR", "message": error_message},
            },
        )

    except Exception as e:
        logger.error(f"Failed to update task due date {task_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Failed to update task due date. Please try again later.",
                },
            },
        )


@router.get(
    "/due/stats",
    response_model=StandardizedResponse[DueDateStatsResponse],
)
async def get_due_date_stats(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> StandardizedResponse[DueDateStatsResponse]:
    """Get statistics for tasks by due date categories.

    Args:
        current_user: Authenticated user.
        session: Database session.

    Returns:
        StandardizedResponse containing due date statistics.
    """
    try:
        service = TaskService(session)

        # Get stats
        stats = await service.get_due_date_stats(user_id=current_user.id)

        logger.info(f"Retrieved due date stats for user_id={current_user.id}")

        return StandardizedResponse(
            success=True, message="Due date statistics retrieved successfully", data=stats
        )

    except Exception as e:
        logger.error(f"Failed to retrieve due date stats: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Failed to retrieve statistics. Please try again later.",
                },
            },
        )


# ============================================================================
# Analytics Routes (Dashboard Statistics)
# ============================================================================


@router.get(
    "/analytics/stats",
    response_model=StandardizedResponse[AnalyticsStatsResponse],
)
async def get_analytics_stats(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> StandardizedResponse[AnalyticsStatsResponse]:
    """Get dashboard statistics for tasks.

    Returns:
        - pending_count: Number of pending tasks
        - completed_today_count: Number of tasks completed today
        - overdue_count: Number of overdue tasks
        - total_count: Total number of active (non-deleted) tasks

    Args:
        current_user: Authenticated user.
        session: Database session.

    Returns:
        StandardizedResponse containing analytics statistics.
    """
    try:
        service = TaskService(session)

        # Get analytics stats
        stats = await service.get_analytics_stats(user_id=current_user.id)

        logger.info(
            f"Retrieved analytics stats for user_id={current_user.id}: "
            f"pending={stats.pending_count}, completed_today={stats.completed_today_count}, "
            f"overdue={stats.overdue_count}, total={stats.total_count}"
        )

        return StandardizedResponse(
            success=True, message="Analytics statistics retrieved successfully", data=stats
        )

    except Exception as e:
        logger.error(f"Failed to retrieve analytics stats: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Failed to retrieve analytics. Please try again later.",
                },
            },
        )


@router.get(
    "/analytics/completion-trend",
    response_model=StandardizedResponse[CompletionTrendResponse],
)
async def get_completion_trend(
    days: int = 7,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> StandardizedResponse[CompletionTrendResponse]:
    """Get completion trend data for the last N days.

    Returns daily data points showing:
    - Number of tasks completed
    - Number of tasks created

    Args:
        days: Number of days to include (default: 7, max: 30).
        current_user: Authenticated user.
        session: Database session.

    Returns:
        StandardizedResponse containing completion trend data.
    """
    try:
        # Validate days parameter
        if days < 1 or days > 30:
            raise ValueError("Days parameter must be between 1 and 30")

        service = TaskService(session)

        # Get completion trend
        trend = await service.get_completion_trend(user_id=current_user.id, days=days)

        logger.info(
            f"Retrieved completion trend for user_id={current_user.id}: {days} days, "
            f"{len(trend.data)} data points"
        )

        return StandardizedResponse(
            success=True, message="Completion trend retrieved successfully", data=trend
        )

    except ValueError as e:
        logger.warning(f"Invalid days parameter: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "error": {"code": "INVALID_PARAMETER", "message": str(e)},
            },
        )

    except Exception as e:
        logger.error(f"Failed to retrieve completion trend: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Failed to retrieve completion trend. Please try again later.",
                },
            },
        )


@router.get(
    "/analytics/priority-breakdown",
    response_model=StandardizedResponse[PriorityBreakdownResponse],
)
async def get_priority_breakdown(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> StandardizedResponse[PriorityBreakdownResponse]:
    """Get breakdown of tasks by priority level.

    Returns counts and percentages for each priority level:
    - low
    - medium
    - high

    Args:
        current_user: Authenticated user.
        session: Database session.

    Returns:
        StandardizedResponse containing priority breakdown data.
    """
    try:
        service = TaskService(session)

        # Get priority breakdown
        breakdown = await service.get_priority_breakdown(user_id=current_user.id)

        logger.info(
            f"Retrieved priority breakdown for user_id={current_user.id}: "
            f"total={breakdown.total} tasks"
        )

        return StandardizedResponse(
            success=True, message="Priority breakdown retrieved successfully", data=breakdown
        )

    except Exception as e:
        logger.error(f"Failed to retrieve priority breakdown: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Failed to retrieve priority breakdown. Please try again later.",
                },
            },
        )


@router.post(
    "/{task_id}/tags",
    status_code=status.HTTP_200_OK,
    response_model=StandardizedResponse[None],
)
async def add_tags_to_task(
    task_id: UUID,
    tag_data: dict,  # Expecting {"tag_ids": [str, str, ...]}
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> StandardizedResponse[None]:
    """Add tags to a task.

    Args:
        task_id: UUID of the task.
        tag_data: Dict containing tag_ids list.
        current_user: Authenticated user.
        session: Database session.

    Returns:
        StandardizedResponse with success message.
    """
    try:
        from src.services.tag_service import TagService

        service = TagService(session)
        tag_ids = tag_data.get("tag_ids", [])

        await service.add_tags_to_task(str(task_id), tag_ids, current_user.id)

        logger.info(f"Tags added to task: task_id={task_id}, user_id={current_user.id}")

        return StandardizedResponse(
            success=True,
            message="Tags added to task successfully",
            data=None,
        )

    except Exception as e:
        logger.error(f"Failed to add tags to task: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Failed to add tags. Please try again later.",
                },
            },
        )


@router.delete(
    "/{task_id}/tags",
    status_code=status.HTTP_200_OK,
    response_model=StandardizedResponse[None],
)
async def remove_tags_from_task(
    task_id: UUID,
    tag_data: dict,  # Expecting {"tag_ids": [str, str, ...]}
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> StandardizedResponse[None]:
    """Remove tags from a task.

    Args:
        task_id: UUID of the task.
        tag_data: Dict containing tag_ids list.
        current_user: Authenticated user.
        session: Database session.

    Returns:
        StandardizedResponse with success message.
    """
    try:
        from src.services.tag_service import TagService

        service = TagService(session)
        tag_ids = tag_data.get("tag_ids", [])

        await service.remove_tags_from_task(str(task_id), tag_ids, current_user.id)

        logger.info(f"Tags removed from task: task_id={task_id}, user_id={current_user.id}")

        return StandardizedResponse(
            success=True,
            message="Tags removed from task successfully",
            data=None,
        )

    except Exception as e:
        logger.error(f"Failed to remove tags from task: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Failed to remove tags. Please try again later.",
                },
            },
        )
