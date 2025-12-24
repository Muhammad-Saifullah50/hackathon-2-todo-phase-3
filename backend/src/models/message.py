"""Message model for chatbot feature."""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Literal
from uuid import UUID, uuid4

from sqlalchemy import DateTime, String, Text
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .conversation import Conversation
    from .user import User


class MessageRole(str, Enum):
    """Enumeration for message sender roles."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class MessageBase(SQLModel):
    """Base fields for Message model.

    Attributes:
        role: Message sender (user, assistant, or system).
        content: Message text content.
    """

    role: Literal["user", "assistant", "system"] = Field(
        sa_type=String(20), description="Message sender: user, assistant, or system"
    )
    content: str = Field(sa_type=Text, description="Message text content")


class Message(MessageBase, table=True):
    """Database model for Message entity.

    Represents a single message in a conversation (user or assistant message).
    Messages persist indefinitely and are never updated after creation.

    Attributes:
        id: Unique UUID identifier for the message.
        conversation_id: Foreign key to the Conversation this message belongs to.
        user_id: Foreign key to the User (same as conversation owner).
        created_at: Timestamp when message was created (immutable).
        conversation: Relationship to the parent Conversation object.
    """

    __tablename__ = "messages"

    id: UUID = Field(
        default_factory=uuid4, primary_key=True, description="Unique identifier for the message"
    )
    conversation_id: UUID = Field(
        foreign_key="conversations.id", index=True, description="Conversation this message belongs to"
    )
    user_id: str = Field(
        foreign_key="user.id", index=True, description="ID of the user (conversation owner)"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_type=DateTime(timezone=True),
        index=True,
        description="Timestamp when message was created",
    )

    # Relationships
    conversation: "Conversation" = Relationship(back_populates="messages")


class MessageCreate(MessageBase):
    """Schema for creating a new message.

    Requires role and content. Conversation ID and user ID are set by the service layer.
    """

    pass


class MessageResponse(MessageBase):
    """Schema for message response payloads.

    Includes system-generated fields like id and timestamp.
    """

    id: UUID
    conversation_id: UUID
    user_id: str
    created_at: datetime

    @classmethod
    def from_message(cls, message: "Message") -> "MessageResponse":
        """Create a MessageResponse from a Message model.

        Args:
            message: The Message model instance.

        Returns:
            MessageResponse instance.
        """
        return cls(
            id=message.id,
            conversation_id=message.conversation_id,
            user_id=message.user_id,
            role=message.role,
            content=message.content,
            created_at=message.created_at,
        )
