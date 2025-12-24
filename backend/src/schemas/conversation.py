"""Pydantic schemas for conversation API endpoints."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ConversationListResponse(BaseModel):
    """Schema for conversation list response.

    Attributes:
        id: Conversation UUID.
        title: Conversation title (optional).
        message_count: Number of messages in conversation.
        created_at: Creation timestamp.
        updated_at: Last update timestamp.
    """

    id: UUID = Field(..., description="Conversation UUID")
    title: str | None = Field(default=None, description="Conversation title")
    message_count: int = Field(default=0, description="Number of messages")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class ConversationDetailResponse(BaseModel):
    """Schema for detailed conversation response.

    Attributes:
        id: Conversation UUID.
        user_id: Owner user ID.
        title: Conversation title (optional).
        message_count: Number of messages in conversation.
        created_at: Creation timestamp.
        updated_at: Last update timestamp.
    """

    id: UUID = Field(..., description="Conversation UUID")
    user_id: str = Field(..., description="Owner user ID")
    title: str | None = Field(default=None, description="Conversation title")
    message_count: int = Field(default=0, description="Number of messages")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class ConversationUpdateRequest(BaseModel):
    """Schema for updating conversation details.

    Attributes:
        title: New conversation title.
    """

    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Conversation title (1-200 characters)",
    )


class ConversationCreateRequest(BaseModel):
    """Schema for creating a new conversation.

    Attributes:
        title: Optional conversation title.
    """

    title: str | None = Field(
        default=None,
        max_length=200,
        description="Optional conversation title",
    )
