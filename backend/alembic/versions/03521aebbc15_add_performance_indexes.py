"""add_performance_indexes

Revision ID: 03521aebbc15
Revises: b9ea8df04fcd
Create Date: 2025-12-23 08:35:10.903322

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '03521aebbc15'
down_revision: Union[str, Sequence[str], None] = 'b9ea8df04fcd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: Add composite indexes for performance optimization."""
    # Composite index for filtering tasks by user and deleted status
    # Improves queries: SELECT * FROM tasks WHERE user_id = ? AND deleted_at IS NULL
    op.create_index(
        'idx_tasks_user_deleted',
        'tasks',
        ['user_id', 'deleted_at'],
        postgresql_where=sa.text('deleted_at IS NULL')
    )

    # Composite index for filtering tasks by user and due date
    # Improves queries: SELECT * FROM tasks WHERE user_id = ? AND due_date BETWEEN ? AND ?
    op.create_index(
        'idx_tasks_user_due_date',
        'tasks',
        ['user_id', 'due_date']
    )


def downgrade() -> None:
    """Downgrade schema: Remove composite indexes."""
    op.drop_index('idx_tasks_user_due_date', table_name='tasks')
    op.drop_index('idx_tasks_user_deleted', table_name='tasks')
