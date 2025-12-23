"""Subtask model for task checklist items."""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import DateTime
from sqlmodel import Field, Relationship, SQLModel


class Subtask(SQLModel, table=True):
    """Subtask model representing a checklist item within a parent task.

    Attributes:
        id: Unique identifier for the subtask
        task_id: Foreign key reference to parent task
        description: Subtask description (1-200 characters)
        is_completed: Whether the subtask is marked as complete
        order_index: Display order within parent task (0-indexed)
        created_at: Timestamp when subtask was created
        updated_at: Timestamp when subtask was last modified
    """

    __tablename__ = "subtasks"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        nullable=False,
        description="Unique identifier for the subtask"
    )

    task_id: UUID = Field(
        foreign_key="tasks.id",
        nullable=False,
        ondelete="CASCADE",
        description="Parent task ID"
    )

    description: str = Field(
        min_length=1,
        max_length=200,
        nullable=False,
        description="Subtask description"
    )

    is_completed: bool = Field(
        default=False,
        nullable=False,
        description="Completion status"
    )

    order_index: int = Field(
        ge=0,
        nullable=False,
        description="Display order (0-indexed)"
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
        nullable=False,
        description="Creation timestamp"
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
        nullable=False,
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
        description="Last update timestamp"
    )

    # Relationship back to parent task
    task: Optional["Task"] = Relationship(back_populates="subtasks")

    def __repr__(self) -> str:
        """String representation of subtask."""
        status = "✅" if self.is_completed else "⬜"
        return f"<Subtask {status} {self.description[:30]}...>"

    class Config:
        """Pydantic model configuration."""
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
