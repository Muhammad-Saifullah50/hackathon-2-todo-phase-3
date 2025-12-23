"""Schemas for tag API operations."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class TagListResponse(BaseModel):
    """Response schema for tag list operations."""

    tags: list["TagWithCount"]


class TagWithCount(BaseModel):
    """Tag response with usage count."""

    id: UUID
    name: str
    color: str
    created_at: datetime
    updated_at: datetime
    task_count: int = 0


class TagAssignRequest(BaseModel):
    """Request schema for assigning tags to a task."""

    tag_ids: list[UUID] = Field(..., min_length=1, max_length=10)


class TagAssignResponse(BaseModel):
    """Response schema for tag assignment operations."""

    tags: list["TagWithCount"]


# Forward reference update
TagListResponse.model_rebuild()
TagAssignResponse.model_rebuild()
