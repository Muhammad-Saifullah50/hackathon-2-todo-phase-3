"""Pydantic schemas for subtask API requests and responses."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class SubtaskBase(BaseModel):
    """Base schema for subtask with common fields."""

    description: str = Field(
        min_length=1,
        max_length=200,
        description="Subtask description",
        examples=["Review pull request", "Write unit tests"]
    )


class SubtaskCreate(SubtaskBase):
    """Schema for creating a new subtask.

    The task_id is taken from the URL path parameter.
    The order_index is automatically assigned by the service.
    """

    order_index: Optional[int] = Field(
        default=None,
        ge=0,
        description="Display order (auto-assigned if not provided)"
    )

    @field_validator('description')
    @classmethod
    def validate_description(cls, v: str) -> str:
        """Validate and sanitize description."""
        v = v.strip()
        if not v:
            raise ValueError("Description cannot be empty or whitespace only")
        if len(v) > 200:
            raise ValueError("Description cannot exceed 200 characters")
        return v


class SubtaskUpdate(BaseModel):
    """Schema for updating an existing subtask.

    All fields are optional to support partial updates.
    """

    description: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=200,
        description="Updated subtask description"
    )
    is_completed: Optional[bool] = Field(
        default=None,
        description="Updated completion status"
    )
    order_index: Optional[int] = Field(
        default=None,
        ge=0,
        description="Updated display order"
    )

    @field_validator('description')
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """Validate and sanitize description if provided."""
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("Description cannot be empty or whitespace only")
            if len(v) > 200:
                raise ValueError("Description cannot exceed 200 characters")
        return v


class SubtaskToggle(BaseModel):
    """Schema for toggling subtask completion status."""

    is_completed: bool = Field(
        description="New completion status",
        examples=[True, False]
    )


class SubtaskReorder(BaseModel):
    """Schema for reordering subtasks within a task."""

    subtask_ids: list[UUID] = Field(
        min_length=1,
        description="Ordered list of subtask IDs in desired sequence",
        examples=[
            [
                "123e4567-e89b-12d3-a456-426614174000",
                "123e4567-e89b-12d3-a456-426614174001",
                "123e4567-e89b-12d3-a456-426614174002"
            ]
        ]
    )


class SubtaskResponse(SubtaskBase):
    """Schema for subtask in API responses."""

    id: UUID = Field(description="Unique subtask identifier")
    task_id: UUID = Field(description="Parent task ID")
    is_completed: bool = Field(description="Completion status")
    order_index: int = Field(description="Display order")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")

    class Config:
        """Pydantic model configuration."""
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "task_id": "123e4567-e89b-12d3-a456-426614174001",
                "description": "Review pull request",
                "is_completed": False,
                "order_index": 0,
                "created_at": "2025-12-21T18:30:00Z",
                "updated_at": "2025-12-21T18:30:00Z"
            }
        }


class SubtaskListResponse(BaseModel):
    """Schema for list of subtasks response."""

    subtasks: list[SubtaskResponse] = Field(
        description="List of subtasks for the parent task"
    )
    total_count: int = Field(
        description="Total number of subtasks"
    )
    completed_count: int = Field(
        description="Number of completed subtasks"
    )
    completion_percentage: float = Field(
        ge=0.0,
        le=100.0,
        description="Completion percentage (0-100)"
    )

    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "subtasks": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "task_id": "123e4567-e89b-12d3-a456-426614174001",
                        "description": "Review pull request",
                        "is_completed": True,
                        "order_index": 0,
                        "created_at": "2025-12-21T18:30:00Z",
                        "updated_at": "2025-12-21T18:35:00Z"
                    },
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174002",
                        "task_id": "123e4567-e89b-12d3-a456-426614174001",
                        "description": "Write unit tests",
                        "is_completed": False,
                        "order_index": 1,
                        "created_at": "2025-12-21T18:31:00Z",
                        "updated_at": "2025-12-21T18:31:00Z"
                    }
                ],
                "total_count": 2,
                "completed_count": 1,
                "completion_percentage": 50.0
            }
        }
