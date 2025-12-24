"""Create ChatKit tables for thread persistence

Revision ID: 20251224_chatkit
Revises: add_conversations_messages
Create Date: 2025-12-24

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '20251224_chatkit'
down_revision: Union[str, Sequence[str], None] = 'add_conversations_messages'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create chat_threads and chat_thread_items tables for ChatKit integration."""

    # Create chat_threads table
    op.create_table(
        'chat_threads',
        sa.Column('id', sa.String(255), primary_key=True),
        sa.Column('user_id', sa.String(255), nullable=True),
        sa.Column('title', sa.String(255), nullable=True),
        sa.Column('metadata', postgresql.JSONB, nullable=False, server_default='{}'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='SET NULL'),
    )

    # Create chat_thread_items table
    op.create_table(
        'chat_thread_items',
        sa.Column('id', sa.String(255), primary_key=True),
        sa.Column('thread_id', sa.String(255), nullable=False),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('role', sa.String(50), nullable=True),
        sa.Column('content', postgresql.JSONB, nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('n_tokens', sa.Integer, nullable=True),
        sa.ForeignKeyConstraint(['thread_id'], ['chat_threads.id'], ondelete='CASCADE'),
        sa.CheckConstraint(
            "type IN ('user_message', 'assistant_message', 'client_tool_call', "
            "'sdk_tool_call', 'sdk_hidden_context', 'end_of_turn', 'message', "
            "'tool_call', 'task', 'workflow', 'attachment')",
            name='check_thread_item_type_valid'
        ),
        sa.CheckConstraint(
            "role IN ('user', 'assistant', 'system') OR role IS NULL",
            name='check_thread_item_role_valid'
        ),
        sa.CheckConstraint(
            "octet_length(content::text) <= 32768",
            name='check_content_size_limit'
        ),
    )

    # Indexes for chat_threads
    op.create_index('idx_chat_threads_user_id', 'chat_threads', ['user_id'])
    op.create_index('idx_chat_threads_created_at', 'chat_threads', [sa.text('created_at DESC')])

    # Indexes for chat_thread_items
    op.create_index('idx_chat_thread_items_thread_id', 'chat_thread_items', ['thread_id'])
    op.create_index('idx_chat_thread_items_thread_created', 'chat_thread_items', ['thread_id', sa.text('created_at')])

    # Create trigger function for updating thread timestamp
    op.execute("""
        CREATE OR REPLACE FUNCTION update_chat_thread_timestamp()
        RETURNS TRIGGER AS $$
        BEGIN
            UPDATE chat_threads SET updated_at = NOW() WHERE id = NEW.thread_id;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Create trigger
    op.execute("""
        CREATE TRIGGER chat_item_update_thread_timestamp
        AFTER INSERT ON chat_thread_items
        FOR EACH ROW EXECUTE FUNCTION update_chat_thread_timestamp();
    """)


def downgrade() -> None:
    """Drop ChatKit tables."""

    # Drop trigger
    op.execute("DROP TRIGGER IF EXISTS chat_item_update_thread_timestamp ON chat_thread_items")
    op.execute("DROP FUNCTION IF EXISTS update_chat_thread_timestamp()")

    # Drop indexes for chat_thread_items
    op.drop_index('idx_chat_thread_items_thread_created', table_name='chat_thread_items')
    op.drop_index('idx_chat_thread_items_thread_id', table_name='chat_thread_items')

    # Drop indexes for chat_threads
    op.drop_index('idx_chat_threads_created_at', table_name='chat_threads')
    op.drop_index('idx_chat_threads_user_id', table_name='chat_threads')

    # Drop tables
    op.drop_table('chat_thread_items')
    op.drop_table('chat_threads')
