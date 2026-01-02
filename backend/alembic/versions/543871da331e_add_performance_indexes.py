"""add_performance_indexes

Revision ID: 543871da331e
Revises: 20251224_chatkit
Create Date: 2026-01-02 16:04:46.865348

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '543871da331e'
down_revision: Union[str, Sequence[str], None] = '20251224_chatkit'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Add composite indexes for query performance."""
    # Create indexes with IF NOT EXISTS equivalent
    # Tasks table indexes
    # Index for filtering active tasks by user (most common query)
    op.create_index(
        'idx_tasks_user_active',
        'tasks',
        ['user_id', 'deleted_at'],
        unique=False,
        if_not_exists=True
    )

    # Index for filtering tasks by status
    op.create_index(
        'idx_tasks_user_status_active',
        'tasks',
        ['user_id', 'status', 'deleted_at'],
        unique=False,
        if_not_exists=True
    )

    # Index for filtering tasks by due date
    op.create_index(
        'idx_tasks_user_due_date',
        'tasks',
        ['user_id', 'due_date', 'deleted_at'],
        unique=False,
        if_not_exists=True
    )

    # Index for task priority filtering
    op.create_index(
        'idx_tasks_user_priority',
        'tasks',
        ['user_id', 'priority', 'deleted_at'],
        unique=False,
        if_not_exists=True
    )

    # Subtasks table indexes
    # Index for efficient subtask ordering within a task
    op.create_index(
        'idx_subtasks_task_order',
        'subtasks',
        ['task_id', 'order_index'],
        unique=False,
        if_not_exists=True
    )

    # Messages table indexes
    # Index for efficient message retrieval in conversations
    op.create_index(
        'idx_messages_conversation_created',
        'messages',
        ['conversation_id', 'created_at'],
        unique=False,
        if_not_exists=True
    )

    # Conversations table indexes
    # Index for listing user conversations by most recent
    op.create_index(
        'idx_conversations_user_updated',
        'conversations',
        ['user_id', 'updated_at'],
        unique=False,
        if_not_exists=True
    )

    # Tags table indexes
    # Index for unique tag names per user
    op.create_index(
        'idx_tags_user_name',
        'tags',
        ['user_id', 'name'],
        unique=True,
        if_not_exists=True
    )


def downgrade() -> None:
    """Downgrade schema - Remove composite indexes."""
    # Drop indexes in reverse order
    op.drop_index('idx_tags_user_name', table_name='tags')
    op.drop_index('idx_conversations_user_updated', table_name='conversations')
    op.drop_index('idx_messages_conversation_created', table_name='messages')
    op.drop_index('idx_subtasks_task_order', table_name='subtasks')
    op.drop_index('idx_tasks_user_priority', table_name='tasks')
    op.drop_index('idx_tasks_user_due_date', table_name='tasks')
    op.drop_index('idx_tasks_user_status_active', table_name='tasks')
    op.drop_index('idx_tasks_user_active', table_name='tasks')
