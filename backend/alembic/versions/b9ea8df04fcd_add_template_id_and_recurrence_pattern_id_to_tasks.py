"""add template_id and recurrence_pattern_id to tasks

Revision ID: b9ea8df04fcd
Revises: 805af8b6195e
Create Date: 2025-12-22 12:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'b9ea8df04fcd'
down_revision: Union[str, Sequence[str], None] = 'bff3b8d45e5b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add template_id as UUID to match task_templates.id
    op.add_column('tasks', sa.Column('template_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key(
        'fk_tasks_template_id_task_templates',
        'tasks', 'task_templates',
        ['template_id'], ['id'],
        ondelete='SET NULL'
    )

    # Add recurrence_pattern_id as UUID to match recurrence_patterns.id
    op.add_column('tasks', sa.Column('recurrence_pattern_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key(
        'fk_tasks_recurrence_pattern_id_recurrence_patterns',
        'tasks', 'recurrence_patterns',
        ['recurrence_pattern_id'], ['id'],
        ondelete='SET NULL'
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('fk_tasks_recurrence_pattern_id_recurrence_patterns', 'tasks', type_='foreignkey')
    op.drop_column('tasks', 'recurrence_pattern_id')
    op.drop_constraint('fk_tasks_template_id_task_templates', 'tasks', type_='foreignkey')
    op.drop_column('tasks', 'template_id')
