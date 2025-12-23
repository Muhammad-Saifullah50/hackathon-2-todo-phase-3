"""Add deleted_at column to tasks table for soft delete functionality

Revision ID: 20251220_104402
Revises: ff71d53c1299
Create Date: 2025-12-20 10:44:02

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20251220_104402'
down_revision: Union[str, None] = 'ff71d53c1299'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add deleted_at column to tasks table with indexes for performance."""
    # Add deleted_at column (nullable timestamp for soft delete)
    op.add_column(
        'tasks',
        sa.Column('deleted_at', sa.TIMESTAMP(timezone=True), nullable=True)
    )

    # Create index on deleted_at for trash queries
    op.create_index(
        'idx_tasks_deleted_at',
        'tasks',
        ['deleted_at']
    )

    # Create composite index for active tasks (most common query)
    # WHERE deleted_at IS NULL optimizes queries for non-deleted tasks
    op.create_index(
        'idx_tasks_user_deleted',
        'tasks',
        ['user_id', 'deleted_at'],
        postgresql_where=sa.text('deleted_at IS NULL')
    )


def downgrade() -> None:
    """Remove deleted_at column and associated indexes."""
    # Drop indexes first
    op.drop_index('idx_tasks_user_deleted', table_name='tasks')
    op.drop_index('idx_tasks_deleted_at', table_name='tasks')

    # Drop column
    op.drop_column('tasks', 'deleted_at')
