"""Template-Tag association model."""

from datetime import datetime, timezone
from uuid import UUID

from sqlmodel import Field, SQLModel


class TemplateTag(SQLModel, table=True):
    """Many-to-many relationship between templates and tags."""

    __tablename__ = "template_tags"

    template_id: str = Field(
        foreign_key="task_templates.id",
        primary_key=True,
        max_length=36,
        ondelete="CASCADE",
        index=True,
    )
    tag_id: UUID = Field(
        foreign_key="tags.id",
        primary_key=True,
        ondelete="CASCADE",
        index=True,
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
