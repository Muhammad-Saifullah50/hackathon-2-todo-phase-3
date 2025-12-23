"""API routes for search and quick filter operations."""

import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import get_current_user
from src.db.session import get_db
from src.models.user import User
from src.schemas.responses import StandardizedResponse
from src.schemas.search_schemas import (
    AutocompleteResponse,
    QuickFilterOption,
    QuickFiltersResponse,
    SearchResponse,
)
from src.services.task_service import TaskService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/tasks", tags=["search"])


@router.get(
    "/search",
    response_model=StandardizedResponse[SearchResponse],
)
async def search_tasks(
    q: str = Query(default="", max_length=100, description="Search query string"),
    status_filter: str | None = Query(
        default=None,
        alias="status",
        description="Filter by status (pending/completed)",
    ),
    priority: str | None = Query(
        default=None, description="Filter by priority (low/medium/high)"
    ),
    tags: str | None = Query(
        default=None, description="Comma-separated list of tag IDs to filter by"
    ),
    due_date_from: str | None = Query(
        default=None, description="Filter tasks due after this date (ISO 8601)"
    ),
    due_date_to: str | None = Query(
        default=None, description="Filter tasks due before this date (ISO 8601)"
    ),
    has_due_date: bool | None = Query(
        default=None, description="Filter tasks with/without due dates"
    ),
    has_notes: bool | None = Query(
        default=None, description="Filter tasks with/without notes"
    ),
    page: int = Query(default=1, ge=1, description="Page number"),
    limit: int = Query(default=20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> StandardizedResponse[SearchResponse]:
    """Search tasks across title, description, and notes fields.

    Combines text search with multiple filter options using AND logic.

    Args:
        q: Search query (searches title, description, notes).
        status_filter: Filter by task status.
        priority: Filter by task priority.
        tags: Comma-separated tag IDs (returns tasks with ANY of the specified tags).
        due_date_from: Filter tasks due after this date.
        due_date_to: Filter tasks due before this date.
        has_due_date: Filter tasks with/without due dates.
        has_notes: Filter tasks with/without notes.
        page: Page number for pagination.
        limit: Items per page.
        current_user: Authenticated user from JWT token.
        session: Database session.

    Returns:
        StandardizedResponse containing search results with pagination.
    """
    try:
        service = TaskService(session)

        # Parse priority if provided
        priority_filter = None
        if priority:
            from src.models.task import TaskPriority

            try:
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

        # Parse status if provided
        status_enum = None
        if status_filter:
            from src.models.task import TaskStatus

            try:
                status_enum = TaskStatus(status_filter.lower())
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "success": False,
                        "error": {
                            "code": "VALIDATION_ERROR",
                            "message": f"Invalid status: {status_filter}. Must be pending or completed",
                        },
                    },
                )

        # Parse due dates if provided
        due_date_from_dt = None
        due_date_to_dt = None

        if due_date_from:
            try:
                due_date_from_dt = datetime.fromisoformat(
                    due_date_from.replace("Z", "+00:00")
                )
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
                due_date_to_dt = datetime.fromisoformat(
                    due_date_to.replace("Z", "+00:00")
                )
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

        # Perform search
        result = await service.search_tasks(
            user_id=current_user.id,
            query=q.strip() if q else None,
            status=status_enum,
            priority=priority_filter,
            tag_ids=tag_ids,
            due_date_from=due_date_from_dt,
            due_date_to=due_date_to_dt,
            has_due_date=has_due_date,
            has_notes=has_notes,
            page=page,
            limit=limit,
        )

        logger.info(
            f"Search completed: user_id={current_user.id}, query='{q}', "
            f"results={len(result.tasks)}"
        )

        return StandardizedResponse(
            success=True,
            message="Search completed successfully",
            data=result,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Search failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Search failed. Please try again later.",
                },
            },
        )


@router.get(
    "/autocomplete",
    response_model=StandardizedResponse[AutocompleteResponse],
)
async def get_autocomplete_suggestions(
    q: str = Query(min_length=1, max_length=100, description="Search query string"),
    limit: int = Query(default=5, ge=1, le=10, description="Maximum suggestions"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> StandardizedResponse[AutocompleteResponse]:
    """Get autocomplete suggestions for task search.

    Returns task titles that match the query prefix for quick selection.

    Args:
        q: Search query prefix.
        limit: Maximum number of suggestions to return.
        current_user: Authenticated user from JWT token.
        session: Database session.

    Returns:
        StandardizedResponse containing list of matching task titles.
    """
    try:
        service = TaskService(session)

        suggestions = await service.get_autocomplete_suggestions(
            user_id=current_user.id,
            query=q.strip(),
            limit=limit,
        )

        logger.info(
            f"Autocomplete: user_id={current_user.id}, query='{q}', "
            f"suggestions={len(suggestions)}"
        )

        return StandardizedResponse(
            success=True,
            message="Suggestions retrieved successfully",
            data=AutocompleteResponse(suggestions=suggestions),
        )

    except Exception as e:
        logger.error(f"Autocomplete failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Failed to get suggestions. Please try again later.",
                },
            },
        )


@router.get(
    "/quick-filters",
    response_model=StandardizedResponse[QuickFiltersResponse],
)
async def get_quick_filters(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> StandardizedResponse[QuickFiltersResponse]:
    """Get quick filter options with task counts.

    Returns predefined filter options (Today, This Week, High Priority, Overdue)
    with the count of tasks matching each filter.

    Args:
        current_user: Authenticated user from JWT token.
        session: Database session.

    Returns:
        StandardizedResponse containing quick filter options with counts.
    """
    try:
        service = TaskService(session)

        filters = await service.get_quick_filter_counts(user_id=current_user.id)

        logger.info(f"Quick filters retrieved: user_id={current_user.id}")

        return StandardizedResponse(
            success=True,
            message="Quick filters retrieved successfully",
            data=QuickFiltersResponse(
                filters=[
                    QuickFilterOption(
                        id="today",
                        label="Today",
                        count=filters["today"],
                        filter_params={"due_date_filter": "today"},
                    ),
                    QuickFilterOption(
                        id="this_week",
                        label="This Week",
                        count=filters["this_week"],
                        filter_params={"due_date_filter": "this_week"},
                    ),
                    QuickFilterOption(
                        id="high_priority",
                        label="High Priority",
                        count=filters["high_priority"],
                        filter_params={"priority": "high"},
                    ),
                    QuickFilterOption(
                        id="overdue",
                        label="Overdue",
                        count=filters["overdue"],
                        filter_params={"due_date_filter": "overdue"},
                    ),
                ]
            ),
        )

    except Exception as e:
        logger.error(f"Quick filters failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Failed to get quick filters. Please try again later.",
                },
            },
        )
