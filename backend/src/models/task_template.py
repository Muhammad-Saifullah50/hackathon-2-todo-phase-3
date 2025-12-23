"""Task template model."""

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional
from uuid import uuid4

from sqlalchemy import JSON, DateTime
from sqlmodel import Field, Relationship, SQLModel

from .template_tag import TemplateTag

if TYPE_CHECKING:
    from .tag import Tag


class TaskTemplate(SQLModel, table=True):
    """Task template for creating reusable task structures."""

    __tablename__ = "task_templates"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True, max_length=36)
    user_id: str = Field(foreign_key="user.id", index=True, max_length=255, ondelete="CASCADE")
    name: str = Field(max_length=100)
    title: str = Field(max_length=100)
    description: Optional[str] = Field(default=None)
    priority: str = Field(max_length=20)
    subtasks_template: Optional[dict] = Field(default=None, sa_type=JSON)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
        nullable=False,
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
        nullable=False,
    )

    # Relationships
    tags: list["Tag"] = Relationship(
        back_populates="templates",
        link_model=TemplateTag,
        sa_relationship_kwargs={"lazy": "selectin"},
    )
