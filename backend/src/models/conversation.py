"""Conversation model for chatbot feature."""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DateTime, String
from sqlmodel import Field, Relationship, SQLModel

from .base import TimestampMixin

if TYPE_CHECKING:
    from .message import Message
    from .user import User


class ConversationBase(SQLModel):
    """Base fields for Conversation model.

    Attributes:
        title: Optional conversation title (first message or AI-generated summary).
    """

    title: str | None = Field(default=None, max_length=200, description="Conversation title")


class Conversation(ConversationBase, TimestampMixin, table=True):
    """Database model for Conversation entity.

    Represents a chat session between a user and the AI chatbot.
    Conversations persist indefinitely to maintain complete history.

    Attributes:
        id: Unique UUID identifier for the conversation.
        user_id: Foreign key to the User who owns this conversation.
        created_at: Timestamp when conversation was created (from TimestampMixin).
        updated_at: Timestamp when conversation was last modified (from TimestampMixin).
        messages: Relationship to Message objects in this conversation.
        user: Relationship to the parent User object.
    """

    __tablename__ = "conversations"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique identifier for the conversation",
    )
    user_id: str = Field(
        foreign_key="user.id", index=True, description="ID of the user who owns this conversation"
    )

    # Relationships
    messages: list["Message"] = Relationship(
        back_populates="conversation",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    user: "User" = Relationship(back_populates="conversations")


class ConversationCreate(ConversationBase):
    """Schema for creating a new conversation.

    Title is optional and can be set later based on first message or AI summary.
    """

    pass


class ConversationResponse(ConversationBase):
    """Schema for conversation response payloads.

    Includes system-generated fields like id and timestamps.
    """

    id: UUID
    user_id: str
    created_at: datetime
    updated_at: datetime
    message_count: int = Field(default=0, description="Number of messages in conversation")

    @classmethod
    def from_conversation(
        cls, conversation: "Conversation", message_count: int = 0
    ) -> "ConversationResponse":
        """Create a ConversationResponse from a Conversation model.

        Args:
            conversation: The Conversation model instance.
            message_count: Number of messages in the conversation.

        Returns:
            ConversationResponse with message count populated.
        """
        return cls(
            id=conversation.id,
            user_id=conversation.user_id,
            title=conversation.title,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
            message_count=message_count,
        )
