"""Conversation service for business logic operations."""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.conversation import Conversation, ConversationCreate, ConversationResponse
from src.models.message import Message


class ConversationService:
    """Service class for conversation-related business logic.

    This service layer separates business logic from the HTTP layer,
    making the code more testable and maintainable.

    Attributes:
        session: The async database session for database operations.
    """

    def __init__(self, session: AsyncSession):
        """Initialize the ConversationService.

        Args:
            session: The async database session.
        """
        self.session = session

    async def create_conversation(
        self, conversation_data: ConversationCreate, user_id: str
    ) -> Conversation:
        """Create a new conversation for the authenticated user.

        Args:
            conversation_data: Validated conversation creation data.
            user_id: ID of the authenticated user from JWT token.

        Returns:
            Created Conversation instance with all fields populated.
        """
        # Create Conversation instance
        conversation = Conversation(
            user_id=user_id,
            title=conversation_data.title,
        )

        # Add to session and commit
        self.session.add(conversation)
        await self.session.commit()
        await self.session.refresh(conversation)

        return conversation

    async def get_conversations(
        self, user_id: str, limit: int = 20, offset: int = 0
    ) -> tuple[list[ConversationResponse], int]:
        """Get paginated conversations for the authenticated user.

        Args:
            user_id: ID of the authenticated user.
            limit: Maximum number of conversations to return (default: 20).
            offset: Number of conversations to skip (default: 0).

        Returns:
            Tuple of (list of ConversationResponse, total count).
        """
        # Query for conversations with message count
        query = (
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
            .offset(offset)
            .limit(limit)
        )

        result = await self.session.execute(query)
        conversations = list(result.scalars().all())

        # Get total count
        count_query = select(func.count(Conversation.id)).where(
            Conversation.user_id == user_id
        )
        total_result = await self.session.execute(count_query)
        total_count = total_result.scalar() or 0

        # Build response with message counts
        conversation_responses = []
        for conv in conversations:
            # Count messages for this conversation
            message_count_query = select(func.count(Message.id)).where(
                Message.conversation_id == conv.id
            )
            message_count_result = await self.session.execute(message_count_query)
            message_count = message_count_result.scalar() or 0

            conversation_responses.append(
                ConversationResponse.from_conversation(conv, message_count=message_count)
            )

        return conversation_responses, total_count

    async def get_conversation_by_id(
        self, conversation_id: UUID, user_id: str
    ) -> Conversation | None:
        """Get a specific conversation by ID.

        Args:
            conversation_id: UUID of the conversation.
            user_id: ID of the authenticated user.

        Returns:
            Conversation instance if found and owned by user, None otherwise.
        """
        query = select(Conversation).where(
            and_(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id,
            )
        )

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def update_conversation_timestamp(
        self, conversation_id: UUID, user_id: str
    ) -> Conversation | None:
        """Update the updated_at timestamp for a conversation.

        Args:
            conversation_id: UUID of the conversation.
            user_id: ID of the authenticated user.

        Returns:
            Updated Conversation instance if found and owned by user, None otherwise.
        """
        conversation = await self.get_conversation_by_id(conversation_id, user_id)
        if not conversation:
            return None

        conversation.updated_at = datetime.now(timezone.utc)
        await self.session.commit()
        await self.session.refresh(conversation)

        return conversation

    async def update_conversation_title(
        self, conversation_id: UUID, user_id: str, title: str
    ) -> Conversation | None:
        """Update the title of a conversation.

        Args:
            conversation_id: UUID of the conversation.
            user_id: ID of the authenticated user.
            title: New title for the conversation.

        Returns:
            Updated Conversation instance if found and owned by user, None otherwise.
        """
        conversation = await self.get_conversation_by_id(conversation_id, user_id)
        if not conversation:
            return None

        conversation.title = title
        conversation.updated_at = datetime.now(timezone.utc)
        await self.session.commit()
        await self.session.refresh(conversation)

        return conversation

    async def delete_conversation(
        self, conversation_id: UUID, user_id: str
    ) -> bool:
        """Delete a conversation and all its messages.

        Args:
            conversation_id: UUID of the conversation.
            user_id: ID of the authenticated user.

        Returns:
            True if conversation was deleted, False if not found or not owned by user.
        """
        conversation = await self.get_conversation_by_id(conversation_id, user_id)
        if not conversation:
            return False

        # Delete conversation (cascade will delete messages)
        await self.session.delete(conversation)
        await self.session.commit()

        return True
