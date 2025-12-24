"""Pydantic schemas for chat API endpoints."""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Schema for chat message request.

    Attributes:
        message: User's input message text.
        conversation_id: Optional conversation ID to continue existing conversation.
    """

    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="User's input message (1-2000 characters)",
    )
    conversation_id: UUID | None = Field(
        default=None,
        description="Optional conversation ID to continue existing conversation",
    )


class ChatStreamEvent(BaseModel):
    """Schema for server-sent events during streaming.

    Attributes:
        type: Event type (token, done, error, tool_call).
        content: Event content (token text, error message, etc.).
        conversation_id: Conversation ID for this stream.
        message_id: Message ID for the assistant response.
    """

    type: Literal["token", "done", "error", "tool_call"] = Field(
        ..., description="Event type"
    )
    content: str | None = Field(default=None, description="Event content")
    conversation_id: UUID | None = Field(default=None, description="Conversation ID")
    message_id: UUID | None = Field(default=None, description="Message ID")
    tool_name: str | None = Field(default=None, description="Tool name if tool_call")
    tool_args: dict | None = Field(default=None, description="Tool arguments if tool_call")


class ChatResponse(BaseModel):
    """Schema for complete chat response (non-streaming).

    Attributes:
        conversation_id: ID of the conversation.
        message_id: ID of the assistant's message.
        content: Full assistant response text.
        created_at: Timestamp of the response.
    """

    conversation_id: UUID = Field(..., description="Conversation ID")
    message_id: UUID = Field(..., description="Message ID")
    content: str = Field(..., description="Full assistant response text")
    created_at: datetime = Field(..., description="Response timestamp")


class ToolInvocation(BaseModel):
    """Schema for tool invocation tracking.

    Attributes:
        tool_name: Name of the tool that was invoked.
        args: Arguments passed to the tool.
        result: Result returned by the tool.
        timestamp: When the tool was invoked.
    """

    tool_name: str = Field(..., description="Tool name")
    args: dict = Field(default_factory=dict, description="Tool arguments")
    result: dict | None = Field(default=None, description="Tool result")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Invocation time")


class ChatContext(BaseModel):
    """Schema for conversation context window.

    Attributes:
        conversation_id: ID of the conversation.
        messages: Last N messages for context.
        message_count: Total number of messages in conversation.
    """

    conversation_id: UUID = Field(..., description="Conversation ID")
    messages: list[dict] = Field(default_factory=list, description="Context messages")
    message_count: int = Field(default=0, description="Total message count")
