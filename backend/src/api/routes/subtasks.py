"""API routes for subtask operations."""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import get_current_user
from src.db.session import get_db
from src.models.user import User
from src.schemas.responses import StandardizedResponse
from src.schemas.subtask_schemas import (
    SubtaskCreate,
    SubtaskListResponse,
    SubtaskReorder,
    SubtaskResponse,
    SubtaskToggle,
    SubtaskUpdate,
)
from src.services.subtask_service import SubtaskNotFoundError, SubtaskService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["subtasks"])


@router.get(
    "/tasks/{task_id}/subtasks",
    status_code=status.HTTP_200_OK,
    response_model=StandardizedResponse[SubtaskListResponse],
)
async def get_subtasks(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> StandardizedResponse[SubtaskListResponse]:
    """Get all subtasks for a task.

    Args:
        task_id: UUID of the parent task.
        current_user: Authenticated user from JWT token.
        session: Database session.

    Returns:
        StandardizedResponse containing list of subtasks with statistics.

    Raises:
        HTTPException: 404 if task not found or access denied, 500 for server errors.
    """
    try:
        # Initialize service
        service = SubtaskService(session)

        # Get subtasks (authorization check included)
        result = await service.get_subtasks(task_id, current_user.id)

        # Log successful retrieval
        logger.info(
            f"Subtasks retrieved: task_id={task_id}, user_id={current_user.id}, count={result.total_count}"
        )

        # Return success response
        return StandardizedResponse(
            success=True, message="Subtasks retrieved successfully", data=result
        )

    except SubtaskNotFoundError as e:
        logger.warning(f"Task not found or access denied: task_id={task_id}, user_id={current_user.id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except Exception as e:
        logger.error(f"Error retrieving subtasks: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve subtasks",
        )


@router.post(
    "/tasks/{task_id}/subtasks",
    status_code=status.HTTP_201_CREATED,
    response_model=StandardizedResponse[SubtaskResponse],
)
async def create_subtask(
    task_id: UUID,
    subtask_data: SubtaskCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> StandardizedResponse[SubtaskResponse]:
    """Create a new subtask for a task.

    Args:
        task_id: UUID of the parent task.
        subtask_data: Subtask creation data (description, optional order_index).
        current_user: Authenticated user from JWT token.
        session: Database session.

    Returns:
        StandardizedResponse containing the created subtask.

    Raises:
        HTTPException: 400 for validation errors, 404 if task not found, 500 for server errors.
    """
    try:
        # Initialize service
        service = SubtaskService(session)

        # Create subtask (authorization check included)
        subtask = await service.create_subtask(task_id, subtask_data, current_user.id)

        # Log successful creation
        logger.info(
            f"Subtask created: id={subtask.id}, task_id={task_id}, user_id={current_user.id}"
        )

        # Return success response
        return StandardizedResponse(
            success=True,
            message="Subtask created successfully",
            data=SubtaskResponse.model_validate(subtask),
        )

    except ValidationError as e:
        logger.warning(f"Validation error creating subtask: {e}")
        errors = []
        for err in e.errors():
            errors.append(
                {
                    "field": ".".join(str(loc) for loc in err["loc"]),
                    "message": err["msg"],
                }
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Validation failed", "errors": errors},
        )

    except SubtaskNotFoundError as e:
        logger.warning(f"Task not found or access denied: task_id={task_id}, user_id={current_user.id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except ValueError as e:
        logger.warning(f"Value error creating subtask: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    except Exception as e:
        logger.error(f"Error creating subtask: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create subtask",
        )


@router.patch(
    "/subtasks/{subtask_id}",
    status_code=status.HTTP_200_OK,
    response_model=StandardizedResponse[SubtaskResponse],
)
async def update_subtask(
    subtask_id: UUID,
    subtask_data: SubtaskUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> StandardizedResponse[SubtaskResponse]:
    """Update an existing subtask.

    Args:
        subtask_id: UUID of the subtask to update.
        subtask_data: Updated subtask data (description, is_completed, order_index - all optional).
        current_user: Authenticated user from JWT token.
        session: Database session.

    Returns:
        StandardizedResponse containing the updated subtask.

    Raises:
        HTTPException: 400 for validation errors, 404 if subtask not found, 500 for server errors.
    """
    try:
        # Initialize service
        service = SubtaskService(session)

        # Update subtask (authorization check included)
        subtask = await service.update_subtask(subtask_id, subtask_data, current_user.id)

        # Log successful update
        logger.info(
            f"Subtask updated: id={subtask_id}, user_id={current_user.id}"
        )

        # Return success response
        return StandardizedResponse(
            success=True,
            message="Subtask updated successfully",
            data=SubtaskResponse.model_validate(subtask),
        )

    except ValidationError as e:
        logger.warning(f"Validation error updating subtask: {e}")
        errors = []
        for err in e.errors():
            errors.append(
                {
                    "field": ".".join(str(loc) for loc in err["loc"]),
                    "message": err["msg"],
                }
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Validation failed", "errors": errors},
        )

    except SubtaskNotFoundError as e:
        logger.warning(f"Subtask not found or access denied: subtask_id={subtask_id}, user_id={current_user.id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except Exception as e:
        logger.error(f"Error updating subtask: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update subtask",
        )


@router.patch(
    "/subtasks/{subtask_id}/toggle",
    status_code=status.HTTP_200_OK,
    response_model=StandardizedResponse[SubtaskResponse],
)
async def toggle_subtask(
    subtask_id: UUID,
    toggle_data: SubtaskToggle,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> StandardizedResponse[SubtaskResponse]:
    """Toggle subtask completion status.

    Args:
        subtask_id: UUID of the subtask to toggle.
        toggle_data: New completion status.
        current_user: Authenticated user from JWT token.
        session: Database session.

    Returns:
        StandardizedResponse containing the updated subtask.

    Raises:
        HTTPException: 404 if subtask not found, 500 for server errors.
    """
    try:
        # Initialize service
        service = SubtaskService(session)

        # Toggle subtask (authorization check included)
        subtask = await service.toggle_subtask(
            subtask_id, toggle_data.is_completed, current_user.id
        )

        # Log successful toggle
        logger.info(
            f"Subtask toggled: id={subtask_id}, is_completed={toggle_data.is_completed}, user_id={current_user.id}"
        )

        # Return success response
        return StandardizedResponse(
            success=True,
            message="Subtask completion status updated successfully",
            data=SubtaskResponse.model_validate(subtask),
        )

    except SubtaskNotFoundError as e:
        logger.warning(f"Subtask not found or access denied: subtask_id={subtask_id}, user_id={current_user.id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except Exception as e:
        logger.error(f"Error toggling subtask: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to toggle subtask completion status",
        )


@router.delete(
    "/subtasks/{subtask_id}",
    status_code=status.HTTP_200_OK,
    response_model=StandardizedResponse[None],
)
async def delete_subtask(
    subtask_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> StandardizedResponse[None]:
    """Delete a subtask.

    Args:
        subtask_id: UUID of the subtask to delete.
        current_user: Authenticated user from JWT token.
        session: Database session.

    Returns:
        StandardizedResponse with no data.

    Raises:
        HTTPException: 404 if subtask not found, 500 for server errors.
    """
    try:
        # Initialize service
        service = SubtaskService(session)

        # Delete subtask (authorization check included)
        await service.delete_subtask(subtask_id, current_user.id)

        # Log successful deletion
        logger.info(f"Subtask deleted: id={subtask_id}, user_id={current_user.id}")

        # Return success response
        return StandardizedResponse(
            success=True, message="Subtask deleted successfully", data=None
        )

    except SubtaskNotFoundError as e:
        logger.warning(f"Subtask not found or access denied: subtask_id={subtask_id}, user_id={current_user.id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except Exception as e:
        logger.error(f"Error deleting subtask: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete subtask",
        )


@router.patch(
    "/tasks/{task_id}/subtasks/reorder",
    status_code=status.HTTP_200_OK,
    response_model=StandardizedResponse[SubtaskListResponse],
)
async def reorder_subtasks(
    task_id: UUID,
    reorder_data: SubtaskReorder,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> StandardizedResponse[SubtaskListResponse]:
    """Reorder subtasks within a task.

    Args:
        task_id: UUID of the parent task.
        reorder_data: List of subtask IDs in desired order.
        current_user: Authenticated user from JWT token.
        session: Database session.

    Returns:
        StandardizedResponse containing updated list of subtasks.

    Raises:
        HTTPException: 400 for validation errors, 404 if task not found, 500 for server errors.
    """
    try:
        # Initialize service
        service = SubtaskService(session)

        # Reorder subtasks (authorization check included)
        subtasks = await service.reorder_subtasks(
            task_id, reorder_data.subtask_ids, current_user.id
        )

        # Get updated statistics
        result = await service.get_subtasks(task_id, current_user.id)

        # Log successful reorder
        logger.info(
            f"Subtasks reordered: task_id={task_id}, user_id={current_user.id}, count={len(subtasks)}"
        )

        # Return success response
        return StandardizedResponse(
            success=True, message="Subtasks reordered successfully", data=result
        )

    except SubtaskNotFoundError as e:
        logger.warning(f"Task not found or access denied: task_id={task_id}, user_id={current_user.id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except ValueError as e:
        logger.warning(f"Value error reordering subtasks: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    except Exception as e:
        logger.error(f"Error reordering subtasks: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reorder subtasks",
        )
