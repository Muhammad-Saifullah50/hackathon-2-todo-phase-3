"""create recurrence patterns table

Revision ID: f11c2362ad64
Revises: 20251221_183345
Create Date: 2025-12-22 08:49:54.533824

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'f11c2362ad64'
down_revision: Union[str, Sequence[str], None] = '20251221_183345'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'recurrence_patterns',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('task_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('frequency', sa.String(length=50), nullable=False),
        sa.Column('interval', sa.Integer(), nullable=False),
        sa.Column('days_of_week', sa.JSON(), nullable=True),
        sa.Column('day_of_month', sa.Integer(), nullable=True),
        sa.Column('end_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('next_occurrence_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('task_id', name='uq_recurrence_pattern_task_id')
    )
    op.create_index('ix_recurrence_patterns_task_id', 'recurrence_patterns', ['task_id'])
    op.create_index('ix_recurrence_patterns_next_occurrence', 'recurrence_patterns', ['next_occurrence_date'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_recurrence_patterns_next_occurrence', table_name='recurrence_patterns')
    op.drop_index('ix_recurrence_patterns_task_id', table_name='recurrence_patterns')
    op.drop_table('recurrence_patterns')
