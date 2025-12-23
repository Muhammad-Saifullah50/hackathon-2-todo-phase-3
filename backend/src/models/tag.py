"""Tag model for task categorization.

This module defines the Tag model for organizing tasks with color-coded labels.
"""

import re
from datetime import datetime
from typing import TYPE_CHECKING, List
from uuid import UUID, uuid4

from pydantic import field_validator
from sqlmodel import Field, Relationship, SQLModel

from .base import TimestampMixin
from .template_tag import TemplateTag

if TYPE_CHECKING:
    from .task import Task
    from .task_tag import TaskTag
    from .user import User
    from .task_template import TaskTemplate


class TagBase(SQLModel):
    """Base fields for Tag model.

    Attributes:
        name: Tag name (1-50 characters).
        color: Hex color code (#RRGGBB format).
    """

    name: str = Field(max_length=50, description="Tag name (unique per user)")
    color: str = Field(max_length=7, description="Hex color code (#RRGGBB)")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate tag name.

        Args:
            v: The name string to validate.

        Returns:
            Trimmed and validated name string.

        Raises:
            ValueError: If name is empty or exceeds 50 characters.
        """
        v = v.strip()
        if not v:
            raise ValueError("Tag name cannot be empty")
        if len(v) > 50:
            raise ValueError("Tag name must be 50 characters or less")
        return v

    @field_validator("color")
    @classmethod
    def validate_color(cls, v: str) -> str:
        """Validate hex color code.

        Args:
            v: The color string to validate.

        Returns:
            Validated color string.

        Raises:
            ValueError: If color is not a valid hex color code.
        """
        if not re.match(r"^#[0-9A-Fa-f]{6}$", v):
            raise ValueError("Color must be a valid hex color code (#RRGGBB)")
        return v.upper()


class Tag(TagBase, TimestampMixin, table=True):
    """Database model for Tag entity.

    Attributes:
        id: Unique UUID identifier for the tag.
        user_id: Foreign key to the User who owns this tag.
        created_at: Timestamp when tag was created (from TimestampMixin).
        updated_at: Timestamp when tag was last modified (from TimestampMixin).
        user: Relationship to the parent User object.
        task_tags: Relationship to TaskTag associations.
    """

    __tablename__ = "tags"

    id: UUID = Field(
        default_factory=uuid4, primary_key=True, description="Unique identifier for the tag"
    )
    user_id: str = Field(
        foreign_key="user.id", index=True, description="ID of the user who owns this tag"
    )

    # Relationships
    user: "User" = Relationship(back_populates="tags")
    task_tags: List["TaskTag"] = Relationship(back_populates="tag", cascade_delete=True)
    templates: List["TaskTemplate"] = Relationship(
        back_populates="tags",
        link_model=TemplateTag,
    )


class TagCreate(TagBase):
    """Schema for creating a new tag.

    Inherits all fields from TagBase with custom validation rules.
    """

    pass


class TagUpdate(SQLModel):
    """Schema for updating an existing tag.

    All fields are optional to allow partial updates.
    """

    name: str | None = None
    color: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str | None) -> str | None:
        """Validate tag name if provided."""
        if v is None:
            return None
        v = v.strip()
        if not v:
            raise ValueError("Tag name cannot be empty")
        if len(v) > 50:
            raise ValueError("Tag name must be 50 characters or less")
        return v

    @field_validator("color")
    @classmethod
    def validate_color(cls, v: str | None) -> str | None:
        """Validate hex color code if provided."""
        if v is None:
            return None
        if not re.match(r"^#[0-9A-Fa-f]{6}$", v):
            raise ValueError("Color must be a valid hex color code (#RRGGBB)")
        return v.upper()


class TagResponse(TagBase):
    """Schema for tag response payloads.

    Includes system-generated fields like id and timestamps.
    """

    id: UUID
    user_id: str
    created_at: datetime
    updated_at: datetime
