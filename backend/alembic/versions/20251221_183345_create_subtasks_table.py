"""Create subtasks table

Revision ID: 20251221_183345
Revises: 20251221_124431
Create Date: 2025-12-21

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '20251221_183345'
down_revision: Union[str, Sequence[str], None] = '20251221_124431'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create subtasks table."""
    op.create_table(
        'subtasks',
        sa.Column('id', sa.Uuid(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('task_id', sa.Uuid(), nullable=False),
        sa.Column('description', sa.String(length=200), nullable=False),
        sa.Column('is_completed', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('order_index', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint("char_length(description) >= 1 AND char_length(description) <= 200", name='ck_subtasks_description_length'),
    )
    op.create_index('ix_subtasks_task_id', 'subtasks', ['task_id', 'order_index'])


def downgrade() -> None:
    """Drop subtasks table."""
    op.drop_index('ix_subtasks_task_id', table_name='subtasks')
    op.drop_table('subtasks')
