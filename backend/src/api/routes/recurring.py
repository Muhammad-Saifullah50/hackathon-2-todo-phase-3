"""API routes for task recurrence management."""

import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import get_current_user
from src.db.session import get_db
from src.models.task import Task
from src.models.user import User
from src.schemas.recurring_schemas import (
    RecurrencePatternCreate,
    RecurrencePatternResponse,
    RecurrencePatternUpdate,
    RecurrencePreviewResponse,
)
from src.services.recurring_service import RecurringService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/tasks", tags=["recurring"])


@router.get("/{task_id}/recurrence", response_model=RecurrencePatternResponse)
async def get_recurrence_pattern(
    task_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> RecurrencePatternResponse:
    """Get recurrence pattern for a task.

    Args:
        task_id: UUID of the task
        db: Database session
        current_user: Authenticated user

    Returns:
        RecurrencePatternResponse with pattern details

    Raises:
        HTTPException: If task not found, not owned by user, or no pattern exists
    """
    try:
        # Verify task exists and belongs to user
        task = await db.get(Task, task_id)
        if not task:
            logger.warning(f"Task not found: task_id={task_id}, user_id={current_user.id}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        if task.user_id != current_user.id:
            logger.warning(f"Unauthorized access to task: task_id={task_id}, user_id={current_user.id}")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this task")

        # Get pattern
        service = RecurringService(db)
        pattern = await service.get_recurrence_pattern(task_id)

        if not pattern:
            logger.info(f"No recurrence pattern found: task_id={task_id}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No recurrence pattern found for this task")

        logger.info(f"Recurrence pattern retrieved: task_id={task_id}, user_id={current_user.id}")
        return RecurrencePatternResponse.model_validate(pattern)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get recurrence pattern: task_id={task_id}, error={str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve recurrence pattern. Please try again later."
        )


@router.post("/{task_id}/recurrence", response_model=RecurrencePatternResponse, status_code=201)
async def create_recurrence_pattern(
    task_id: UUID,
    pattern_data: RecurrencePatternCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> RecurrencePatternResponse:
    """Create a recurrence pattern for a task.

    Args:
        task_id: UUID of the task
        pattern_data: Recurrence pattern configuration
        db: Database session
        current_user: Authenticated user

    Returns:
        Created RecurrencePatternResponse

    Raises:
        HTTPException: If task not found, not owned by user, or validation fails
    """
    # Verify task exists and belongs to user
    task = await db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this task")

    # Create pattern
    service = RecurringService(db)
    try:
        pattern = await service.create_recurrence_pattern(
            task_id=task_id,
            pattern_data=pattern_data,
            start_date=task.due_date
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return RecurrencePatternResponse.model_validate(pattern)


@router.patch("/{task_id}/recurrence", response_model=RecurrencePatternResponse)
async def update_recurrence_pattern(
    task_id: UUID,
    pattern_data: RecurrencePatternUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> RecurrencePatternResponse:
    """Update a recurrence pattern for a task.

    Args:
        task_id: UUID of the task
        pattern_data: Updated pattern configuration
        db: Database session
        current_user: Authenticated user

    Returns:
        Updated RecurrencePatternResponse

    Raises:
        HTTPException: If task/pattern not found, not owned by user, or validation fails
    """
    # Verify task exists and belongs to user
    task = await db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this task")

    # Update pattern
    service = RecurringService(db)
    try:
        pattern = await service.update_recurrence_pattern(task_id, pattern_data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return RecurrencePatternResponse.model_validate(pattern)


@router.delete("/{task_id}/recurrence", status_code=204)
async def delete_recurrence_pattern(
    task_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    """Delete a recurrence pattern for a task (stops recurrence).

    Args:
        task_id: UUID of the task
        db: Database session
        current_user: Authenticated user

    Raises:
        HTTPException: If task not found, not owned by user, or no pattern exists
    """
    # Verify task exists and belongs to user
    task = await db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this task")

    # Delete pattern
    service = RecurringService(db)
    deleted = await service.delete_recurrence_pattern(task_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="No recurrence pattern found for this task")


@router.get("/{task_id}/recurrence/preview", response_model=RecurrencePreviewResponse)
async def preview_recurrence_occurrences(
    task_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    count: Annotated[int, Query(ge=1, le=20)] = 5,
) -> RecurrencePreviewResponse:
    """Preview the next N occurrences of a recurring task.

    Args:
        task_id: UUID of the task
        count: Number of occurrences to preview (1-20, default 5)
        db: Database session
        current_user: Authenticated user

    Returns:
        RecurrencePreviewResponse with upcoming dates

    Raises:
        HTTPException: If task/pattern not found or not owned by user
    """
    # Verify task exists and belongs to user
    task = await db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this task")

    # Get preview
    service = RecurringService(db)
    try:
        preview = await service.preview_occurrences(task_id, count)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return preview
