"""API routes for tag operations."""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import get_current_user
from src.db.session import get_db
from src.models.tag import TagCreate, TagResponse, TagUpdate
from src.models.user import User
from src.schemas.responses import StandardizedResponse
from src.schemas.tag_schemas import (
    TagAssignRequest,
    TagAssignResponse,
    TagListResponse,
    TagWithCount,
)
from src.services.tag_service import TagService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/tags", tags=["tags"])


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=StandardizedResponse[TagListResponse],
)
async def get_tags(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> StandardizedResponse[TagListResponse]:
    """Get all tags for the authenticated user.

    Args:
        current_user: Authenticated user from JWT token.
        session: Database session.

    Returns:
        StandardizedResponse containing tag list with usage counts.
    """
    try:
        service = TagService(session)

        # Get tags
        tags = await service.get_tags(user_id=current_user.id)

        # Get usage counts for each tag
        tags_with_counts = []
        for tag in tags:
            count = await service.get_tag_usage_count(str(tag.id), current_user.id)
            tags_with_counts.append(
                TagWithCount(
                    id=tag.id,
                    name=tag.name,
                    color=tag.color,
                    created_at=tag.created_at,
                    updated_at=tag.updated_at,
                    task_count=count,
                )
            )

        logger.info(f"Tags retrieved: user_id={current_user.id}, count={len(tags)}")

        return StandardizedResponse(
            success=True,
            message="Tags retrieved successfully",
            data=TagListResponse(tags=tags_with_counts),
        )

    except Exception as e:
        logger.error(f"Failed to retrieve tags: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Failed to retrieve tags. Please try again later.",
                },
            },
        )


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=StandardizedResponse[TagResponse],
)
async def create_tag(
    tag_data: TagCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> StandardizedResponse[TagResponse]:
    """Create a new tag for the authenticated user.

    Args:
        tag_data: Tag creation data (name, color).
        current_user: Authenticated user from JWT token.
        session: Database session.

    Returns:
        StandardizedResponse containing the created tag.

    Raises:
        HTTPException: 400 for validation errors, 409 for duplicates.
    """
    try:
        service = TagService(session)

        # Create tag
        tag = await service.create_tag(tag_data, current_user.id)

        logger.info(f"Tag created: id={tag.id}, user_id={current_user.id}, name={tag.name}")

        return StandardizedResponse(
            success=True,
            message="Tag created successfully",
            data=TagResponse.model_validate(tag),
        )

    except ValidationError as e:
        logger.warning(f"Validation error creating tag: {e}")
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
        error_message = str(e)
        logger.warning(f"Value error creating tag: {error_message}")

        if "already exists" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "success": False,
                    "error": {
                        "code": "DUPLICATE_TAG",
                        "message": error_message,
                    },
                },
            )

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
        logger.error(f"Failed to create tag: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Failed to create tag. Please try again later.",
                },
            },
        )


@router.patch(
    "/{tag_id}",
    status_code=status.HTTP_200_OK,
    response_model=StandardizedResponse[TagResponse],
)
async def update_tag(
    tag_id: UUID,
    tag_data: TagUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> StandardizedResponse[TagResponse]:
    """Update a tag's name and/or color.

    Args:
        tag_id: UUID of the tag to update.
        tag_data: Tag update data (name and/or color).
        current_user: Authenticated user from JWT token.
        session: Database session.

    Returns:
        StandardizedResponse containing the updated tag.

    Raises:
        HTTPException: 400 for validation errors, 404 for not found, 409 for duplicates.
    """
    try:
        service = TagService(session)

        # Update tag
        tag = await service.update_tag(str(tag_id), current_user.id, tag_data)

        logger.info(f"Tag updated: id={tag_id}, user_id={current_user.id}")

        return StandardizedResponse(
            success=True,
            message="Tag updated successfully",
            data=TagResponse.model_validate(tag),
        )

    except ValueError as e:
        error_message = str(e)
        logger.warning(f"Validation error updating tag {tag_id}: {error_message}")

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

        if "already exists" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "success": False,
                    "error": {
                        "code": "DUPLICATE_TAG",
                        "message": error_message,
                    },
                },
            )

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
        logger.error(f"Failed to update tag {tag_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Failed to update tag. Please try again later.",
                },
            },
        )


@router.delete(
    "/{tag_id}",
    status_code=status.HTTP_200_OK,
    response_model=StandardizedResponse[dict],
)
async def delete_tag(
    tag_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> StandardizedResponse[dict]:
    """Delete a tag and all its task associations.

    Args:
        tag_id: UUID of the tag to delete.
        current_user: Authenticated user from JWT token.
        session: Database session.

    Returns:
        StandardizedResponse with success message.

    Raises:
        HTTPException: 404 for not found.
    """
    try:
        service = TagService(session)

        # Delete tag
        await service.delete_tag(str(tag_id), current_user.id)

        logger.info(f"Tag deleted: id={tag_id}, user_id={current_user.id}")

        return StandardizedResponse(
            success=True,
            message="Tag deleted successfully",
            data={"tag_id": str(tag_id)},
        )

    except ValueError as e:
        error_message = str(e)
        logger.warning(f"Error deleting tag {tag_id}: {error_message}")

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
        logger.error(f"Failed to delete tag {tag_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Failed to delete tag. Please try again later.",
                },
            },
        )


# ============================================================================
# Task Tag Assignment Routes
# ============================================================================


@router.post(
    "/tasks/{task_id}/tags",
    status_code=status.HTTP_200_OK,
    response_model=StandardizedResponse[TagAssignResponse],
)
async def assign_tags_to_task(
    task_id: UUID,
    request: TagAssignRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> StandardizedResponse[TagAssignResponse]:
    """Add tags to a task.

    Args:
        task_id: UUID of the task.
        request: Tag assignment request with tag IDs.
        current_user: Authenticated user from JWT token.
        session: Database session.

    Returns:
        StandardizedResponse containing all tags now associated with the task.

    Raises:
        HTTPException: 400 for validation errors, 404 for not found.
    """
    try:
        service = TagService(session)

        # Add tags to task
        tag_ids = [str(tag_id) for tag_id in request.tag_ids]
        tags = await service.add_tags_to_task(str(task_id), tag_ids, current_user.id)

        # Get counts for response
        tags_with_counts = []
        for tag in tags:
            count = await service.get_tag_usage_count(str(tag.id), current_user.id)
            tags_with_counts.append(
                TagWithCount(
                    id=tag.id,
                    name=tag.name,
                    color=tag.color,
                    created_at=tag.created_at,
                    updated_at=tag.updated_at,
                    task_count=count,
                )
            )

        logger.info(f"Tags assigned to task: task_id={task_id}, tags={len(tags)}")

        return StandardizedResponse(
            success=True,
            message="Tags assigned successfully",
            data=TagAssignResponse(tags=tags_with_counts),
        )

    except ValueError as e:
        error_message = str(e)
        logger.warning(f"Error assigning tags to task {task_id}: {error_message}")

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
        logger.error(f"Failed to assign tags to task {task_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Failed to assign tags. Please try again later.",
                },
            },
        )


@router.delete(
    "/tasks/{task_id}/tags",
    status_code=status.HTTP_200_OK,
    response_model=StandardizedResponse[TagAssignResponse],
)
async def remove_tags_from_task(
    task_id: UUID,
    request: TagAssignRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> StandardizedResponse[TagAssignResponse]:
    """Remove tags from a task.

    Args:
        task_id: UUID of the task.
        request: Tag removal request with tag IDs.
        current_user: Authenticated user from JWT token.
        session: Database session.

    Returns:
        StandardizedResponse containing remaining tags associated with the task.

    Raises:
        HTTPException: 400 for validation errors, 404 for not found.
    """
    try:
        service = TagService(session)

        # Remove tags from task
        tag_ids = [str(tag_id) for tag_id in request.tag_ids]
        tags = await service.remove_tags_from_task(str(task_id), tag_ids, current_user.id)

        # Get counts for response
        tags_with_counts = []
        for tag in tags:
            count = await service.get_tag_usage_count(str(tag.id), current_user.id)
            tags_with_counts.append(
                TagWithCount(
                    id=tag.id,
                    name=tag.name,
                    color=tag.color,
                    created_at=tag.created_at,
                    updated_at=tag.updated_at,
                    task_count=count,
                )
            )

        logger.info(f"Tags removed from task: task_id={task_id}")

        return StandardizedResponse(
            success=True,
            message="Tags removed successfully",
            data=TagAssignResponse(tags=tags_with_counts),
        )

    except ValueError as e:
        error_message = str(e)
        logger.warning(f"Error removing tags from task {task_id}: {error_message}")

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
        logger.error(f"Failed to remove tags from task {task_id}: {str(e)}", exc_info=True)
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


@router.get(
    "/tasks/{task_id}/tags",
    status_code=status.HTTP_200_OK,
    response_model=StandardizedResponse[TagAssignResponse],
)
async def get_task_tags(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> StandardizedResponse[TagAssignResponse]:
    """Get all tags for a specific task.

    Args:
        task_id: UUID of the task.
        current_user: Authenticated user from JWT token.
        session: Database session.

    Returns:
        StandardizedResponse containing tags associated with the task.
    """
    try:
        service = TagService(session)

        # Get task tags
        tags = await service.get_task_tags(str(task_id), current_user.id)

        # Get counts for response
        tags_with_counts = []
        for tag in tags:
            count = await service.get_tag_usage_count(str(tag.id), current_user.id)
            tags_with_counts.append(
                TagWithCount(
                    id=tag.id,
                    name=tag.name,
                    color=tag.color,
                    created_at=tag.created_at,
                    updated_at=tag.updated_at,
                    task_count=count,
                )
            )

        logger.info(f"Task tags retrieved: task_id={task_id}, count={len(tags)}")

        return StandardizedResponse(
            success=True,
            message="Task tags retrieved successfully",
            data=TagAssignResponse(tags=tags_with_counts),
        )

    except Exception as e:
        logger.error(f"Failed to get task tags {task_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Failed to retrieve task tags. Please try again later.",
                },
            },
        )
