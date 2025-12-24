"""Message service for business logic operations."""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.message import Message, MessageCreate, MessageResponse


class MessageService:
    """Service class for message-related business logic.

    This service layer separates business logic from the HTTP layer,
    making the code more testable and maintainable.

    Attributes:
        session: The async database session for database operations.
    """

    def __init__(self, session: AsyncSession):
        """Initialize the MessageService.

        Args:
            session: The async database session.
        """
        self.session = session

    async def create_message(
        self,
        message_data: MessageCreate,
        conversation_id: UUID,
        user_id: str,
    ) -> Message:
        """Create a new message in a conversation.

        Args:
            message_data: Validated message creation data.
            conversation_id: UUID of the conversation.
            user_id: ID of the authenticated user.

        Returns:
            Created Message instance with all fields populated.
        """
        # Create Message instance
        message = Message(
            conversation_id=conversation_id,
            user_id=user_id,
            role=message_data.role,
            content=message_data.content,
        )

        # Add to session and commit
        self.session.add(message)
        await self.session.commit()
        await self.session.refresh(message)

        return message

    async def get_messages(
        self,
        conversation_id: UUID,
        user_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[Message], int]:
        """Get paginated messages for a conversation.

        Args:
            conversation_id: UUID of the conversation.
            user_id: ID of the authenticated user.
            limit: Maximum number of messages to return (default: 50).
            offset: Number of messages to skip (default: 0).

        Returns:
            Tuple of (list of Message instances oldest first, total count).
        """
        # Query for messages (most recent first, then reversed)
        query = (
            select(Message)
            .where(
                and_(
                    Message.conversation_id == conversation_id,
                    Message.user_id == user_id,
                )
            )
            .order_by(Message.created_at.desc())
            .offset(offset)
            .limit(limit)
        )

        result = await self.session.execute(query)
        messages = list(result.scalars().all())

        # Reverse to get oldest first (chronological order)
        messages.reverse()

        # Get total count
        count_query = select(func.count(Message.id)).where(
            and_(
                Message.conversation_id == conversation_id,
                Message.user_id == user_id,
            )
        )
        total_result = await self.session.execute(count_query)
        total_count = total_result.scalar() or 0

        return messages, total_count

    async def get_conversation_context(
        self,
        conversation_id: UUID,
        user_id: str,
        limit: int = 50,
    ) -> list[Message]:
        """Get last N messages for AI context (oldest first).

        Args:
            conversation_id: UUID of the conversation.
            user_id: ID of the authenticated user.
            limit: Maximum number of messages to return (default: 50).

        Returns:
            List of Message instances in chronological order (oldest first).
        """
        messages, _ = await self.get_messages(
            conversation_id=conversation_id,
            user_id=user_id,
            limit=limit,
            offset=0,
        )
        return messages

    async def get_message_by_id(
        self, message_id: UUID, user_id: str
    ) -> Message | None:
        """Get a specific message by ID.

        Args:
            message_id: UUID of the message.
            user_id: ID of the authenticated user.

        Returns:
            Message instance if found and owned by user, None otherwise.
        """
        query = select(Message).where(
            and_(
                Message.id == message_id,
                Message.user_id == user_id,
            )
        )

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_messages_count(
        self, conversation_id: UUID, user_id: str
    ) -> int:
        """Get total message count for a conversation.

        Args:
            conversation_id: UUID of the conversation.
            user_id: ID of the authenticated user.

        Returns:
            Total number of messages in the conversation.
        """
        count_query = select(func.count(Message.id)).where(
            and_(
                Message.conversation_id == conversation_id,
                Message.user_id == user_id,
            )
        )
        result = await self.session.execute(count_query)
        return result.scalar() or 0
