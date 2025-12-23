"""Template schemas for request/response validation."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class SubtaskTemplateItem(BaseModel):
    """Subtask template item."""

    description: str = Field(..., min_length=1, max_length=200)


class TemplateCreate(BaseModel):
    """Schema for creating a new template."""

    name: str = Field(..., min_length=1, max_length=100)
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    priority: str = Field(..., pattern="^(low|medium|high)$")
    subtasks_template: Optional[list[SubtaskTemplateItem]] = None
    tag_ids: Optional[list[str]] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate template name."""
        if not v or not v.strip():
            raise ValueError("Template name cannot be empty")
        return v.strip()

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate template title."""
        if not v or not v.strip():
            raise ValueError("Template title cannot be empty")
        return v.strip()


class TemplateUpdate(BaseModel):
    """Schema for updating an existing template."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    priority: Optional[str] = Field(None, pattern="^(low|medium|high)$")
    subtasks_template: Optional[list[SubtaskTemplateItem]] = None
    tag_ids: Optional[list[str]] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate template name."""
        if v is not None and (not v or not v.strip()):
            raise ValueError("Template name cannot be empty")
        return v.strip() if v else v

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        """Validate template title."""
        if v is not None and (not v or not v.strip()):
            raise ValueError("Template title cannot be empty")
        return v.strip() if v else v


class TemplateTagResponse(BaseModel):
    """Schema for tag in template response."""

    id: str
    name: str
    color: str


class TemplateResponse(BaseModel):
    """Schema for template in responses."""

    id: str
    user_id: str
    name: str
    title: str
    description: Optional[str] = None
    priority: str
    subtasks_template: Optional[list[SubtaskTemplateItem]] = None
    tags: list[TemplateTagResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TemplateListResponse(BaseModel):
    """Schema for paginated template list."""

    templates: list[TemplateResponse]
    total: int
    page: int
    page_size: int
