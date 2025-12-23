"""TaskTag join model for many-to-many task-tag relationships.

This module defines the TaskTag model that links tasks with tags.
"""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, func
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .tag import Tag
    from .task import Task


class TaskTag(SQLModel, table=True):
    """Database model for Task-Tag join table.

    This model represents the many-to-many relationship between tasks and tags.

    Attributes:
        task_id: Foreign key to the Task.
        tag_id: Foreign key to the Tag.
        created_at: Timestamp when the association was created.
        task: Relationship to the Task object.
        tag: Relationship to the Tag object.
    """

    __tablename__ = "task_tags"

    task_id: UUID = Field(
        foreign_key="tasks.id",
        primary_key=True,
        description="ID of the associated task",
    )
    tag_id: UUID = Field(
        foreign_key="tags.id",
        primary_key=True,
        description="ID of the associated tag",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(),
        sa_type=DateTime(timezone=True),
        sa_column_kwargs={
            "server_default": func.now(),
        },
        description="Timestamp when the association was created",
    )

    # Relationships
    task: "Task" = Relationship(back_populates="task_tags")
    tag: "Tag" = Relationship(back_populates="task_tags")
