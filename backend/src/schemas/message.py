"""Pydantic schemas for message API endpoints."""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class MessageListResponse(BaseModel):
    """Schema for message list response.

    Attributes:
        id: Message UUID.
        conversation_id: Parent conversation UUID.
        role: Message sender role (user, assistant, system).
        content: Message text content.
        created_at: Creation timestamp.
    """

    id: UUID = Field(..., description="Message UUID")
    conversation_id: UUID = Field(..., description="Conversation UUID")
    role: Literal["user", "assistant", "system"] = Field(..., description="Message role")
    content: str = Field(..., description="Message text content")
    created_at: datetime = Field(..., description="Creation timestamp")


class MessageDetailResponse(BaseModel):
    """Schema for detailed message response.

    Attributes:
        id: Message UUID.
        conversation_id: Parent conversation UUID.
        user_id: Owner user ID.
        role: Message sender role (user, assistant, system).
        content: Message text content.
        created_at: Creation timestamp.
    """

    id: UUID = Field(..., description="Message UUID")
    conversation_id: UUID = Field(..., description="Conversation UUID")
    user_id: str = Field(..., description="Owner user ID")
    role: Literal["user", "assistant", "system"] = Field(..., description="Message role")
    content: str = Field(..., description="Message text content")
    created_at: datetime = Field(..., description="Creation timestamp")


class MessageCreateRequest(BaseModel):
    """Schema for creating a new message.

    Attributes:
        role: Message sender role (user, assistant, system).
        content: Message text content.
    """

    role: Literal["user", "assistant", "system"] = Field(..., description="Message role")
    content: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="Message content (1-10000 characters)",
    )
