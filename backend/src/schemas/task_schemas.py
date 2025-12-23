"""Request and response schemas for task management operations."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from ..models.task import TaskResponse, TaskStatus


class TaskMetadata(BaseModel):
    """Metadata about task counts.

    Attributes:
        total_pending: Number of pending tasks.
        total_completed: Number of completed tasks.
        total_active: Number of active (non-deleted) tasks.
        total_deleted: Number of soft-deleted tasks.
    """

    total_pending: int = Field(ge=0, description="Number of pending tasks")
    total_completed: int = Field(ge=0, description="Number of completed tasks")
    total_active: int = Field(ge=0, description="Number of active (non-deleted) tasks")
    total_deleted: int = Field(ge=0, description="Number of soft-deleted tasks")


class PaginationInfo(BaseModel):
    """Pagination metadata for list responses.

    Attributes:
        page: Current page number (1-indexed).
        limit: Maximum items per page.
        total_items: Total number of items available.
        total_pages: Total number of pages available.
        has_next: Whether there is a next page.
        has_prev: Whether there is a previous page.
    """

    page: int = Field(ge=1, description="Current page number (1-indexed)")
    limit: int = Field(ge=1, le=100, description="Maximum items per page")
    total_items: int = Field(ge=0, description="Total number of items available")
    total_pages: int = Field(ge=0, description="Total number of pages available")
    has_next: bool = Field(description="Whether there is a next page")
    has_prev: bool = Field(description="Whether there is a previous page")


class TaskListResponse(BaseModel):
    """Response schema for task list queries.

    Attributes:
        tasks: List of tasks on the current page.
        metadata: Task count statistics.
        pagination: Pagination information.
    """

    tasks: list[TaskResponse] = Field(description="List of tasks on the current page")
    metadata: TaskMetadata = Field(description="Task count statistics")
    pagination: PaginationInfo = Field(description="Pagination information")


class TaskUpdateRequest(BaseModel):
    """Request schema for updating a task.

    At least one field must be provided. Values must differ from current values.

    Attributes:
        title: New task title (optional).
        description: New task description (optional).
        due_date: New task due date (optional).
        notes: New task notes (optional, markdown supported).
        manual_order: New manual sort order (optional).
    """

    title: str | None = Field(default=None, min_length=1, max_length=100, description="New task title")
    description: str | None = Field(default=None, max_length=500, description="New task description")
    due_date: datetime | None = Field(default=None, description="New task due date (UTC)")
    notes: str | None = Field(default=None, description="New task notes (markdown supported)")
    manual_order: int | None = Field(default=None, ge=0, description="New manual sort order")

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str | None) -> str | None:
        """Validate and trim title if provided."""
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("Title cannot be empty")
        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str | None) -> str | None:
        """Validate and trim description if provided."""
        if v is not None:
            v = v.strip()
            if not v:
                return None  # Convert empty string to None
        return v

    @field_validator("notes")
    @classmethod
    def validate_notes(cls, v: str | None) -> str | None:
        """Validate and trim notes if provided."""
        if v is not None:
            v = v.strip()
            if not v:
                return None  # Convert empty string to None
        return v


class BulkToggleRequest(BaseModel):
    """Request schema for bulk status toggle operations.

    Attributes:
        task_ids: List of task UUIDs to toggle (max 50).
        target_status: The status to set for all tasks.
    """

    task_ids: list[UUID] = Field(
        min_length=1, max_length=50, description="List of task UUIDs to toggle (max 50)"
    )
    target_status: TaskStatus = Field(description="The status to set for all tasks")

    @field_validator("task_ids")
    @classmethod
    def validate_task_ids(cls, v: list[UUID]) -> list[UUID]:
        """Validate task ID list for duplicates and length."""
        if len(v) > 50:
            raise ValueError("Maximum 50 tasks per bulk operation")
        if len(v) != len(set(v)):
            raise ValueError("Duplicate task IDs not allowed")
        return v


class BulkDeleteRequest(BaseModel):
    """Request schema for bulk delete operations.

    Attributes:
        task_ids: List of task UUIDs to delete (max 50).
    """

    task_ids: list[UUID] = Field(
        min_length=1, max_length=50, description="List of task UUIDs to delete (max 50)"
    )

    @field_validator("task_ids")
    @classmethod
    def validate_task_ids(cls, v: list[UUID]) -> list[UUID]:
        """Validate task ID list for duplicates and length."""
        if len(v) > 50:
            raise ValueError("Maximum 50 tasks per bulk operation")
        if len(v) != len(set(v)):
            raise ValueError("Duplicate task IDs not allowed")
        return v


class BulkOperationResponse(BaseModel):
    """Response schema for bulk operations.

    Attributes:
        updated_count: Number of tasks successfully updated.
        tasks: List of updated tasks.
    """

    updated_count: int = Field(ge=0, description="Number of tasks successfully updated")
    tasks: list[TaskResponse] = Field(description="List of updated tasks")


class ReorderTasksRequest(BaseModel):
    """Request schema for reordering tasks.

    Attributes:
        task_ids: Ordered list of task UUIDs representing the new order.
    """

    task_ids: list[UUID] = Field(
        min_length=1,
        max_length=100,
        description="Ordered list of task UUIDs representing the new order",
    )

    @field_validator("task_ids")
    @classmethod
    def validate_task_ids(cls, v: list[UUID]) -> list[UUID]:
        """Validate task ID list for duplicates and length."""
        if len(v) > 100:
            raise ValueError("Maximum 100 tasks per reorder operation")
        if len(v) != len(set(v)):
            raise ValueError("Duplicate task IDs not allowed")
        return v


class DueDateStatsResponse(BaseModel):
    """Response schema for due date statistics.

    Attributes:
        overdue_count: Number of overdue tasks.
        due_today_count: Number of tasks due today.
        due_this_week_count: Number of tasks due this week.
        no_due_date_count: Number of tasks without a due date.
    """

    overdue_count: int = Field(ge=0, description="Number of overdue tasks")
    due_today_count: int = Field(ge=0, description="Number of tasks due today")
    due_this_week_count: int = Field(ge=0, description="Number of tasks due this week")
    no_due_date_count: int = Field(ge=0, description="Number of tasks without a due date")


class UpdateDueDateRequest(BaseModel):
    """Request schema for updating task due date.

    Attributes:
        due_date: New due date (ISO 8601 format with timezone) or None to remove.
    """

    due_date: datetime | None = Field(
        default=None, description="New due date (ISO 8601 with timezone) or None to remove"
    )


# ============================================================================
# Analytics Schemas
# ============================================================================


class AnalyticsStatsResponse(BaseModel):
    """Response schema for dashboard stats.

    Attributes:
        pending_count: Number of pending tasks.
        completed_today_count: Number of tasks completed today.
        overdue_count: Number of overdue tasks.
        total_count: Total number of active tasks.
    """

    pending_count: int = Field(ge=0, description="Number of pending tasks")
    completed_today_count: int = Field(ge=0, description="Number of tasks completed today")
    overdue_count: int = Field(ge=0, description="Number of overdue tasks")
    total_count: int = Field(ge=0, description="Total number of active tasks")


class CompletionTrendDataPoint(BaseModel):
    """Single data point for completion trend.

    Attributes:
        date: Date string (YYYY-MM-DD).
        completed: Number of tasks completed on this date.
        created: Number of tasks created on this date.
    """

    date: str = Field(description="Date string (YYYY-MM-DD)")
    completed: int = Field(ge=0, description="Number of tasks completed")
    created: int = Field(ge=0, description="Number of tasks created")


class CompletionTrendResponse(BaseModel):
    """Response schema for completion trend.

    Attributes:
        data: List of daily completion data points.
        days: Number of days in the trend.
    """

    data: list[CompletionTrendDataPoint] = Field(description="Daily completion data")
    days: int = Field(ge=1, le=30, description="Number of days in trend")


class PriorityBreakdownItem(BaseModel):
    """Single priority breakdown item.

    Attributes:
        priority: Priority level (low, medium, high).
        count: Number of tasks with this priority.
        percentage: Percentage of total tasks.
    """

    priority: str = Field(description="Priority level")
    count: int = Field(ge=0, description="Number of tasks")
    percentage: float = Field(ge=0, le=100, description="Percentage of total")


class PriorityBreakdownResponse(BaseModel):
    """Response schema for priority breakdown.

    Attributes:
        data: List of priority breakdown items.
        total: Total number of tasks.
    """

    data: list[PriorityBreakdownItem] = Field(description="Priority breakdown data")
    total: int = Field(ge=0, description="Total number of tasks")
