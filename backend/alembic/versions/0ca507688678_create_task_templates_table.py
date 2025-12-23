"""create task templates table

Revision ID: 0ca507688678
Revises: f11c2362ad64
Create Date: 2025-12-22 09:34:38.634316

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '0ca507688678'
down_revision: Union[str, Sequence[str], None] = 'f11c2362ad64'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create task_templates table
    op.create_table(
        'task_templates',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('title', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('priority', sa.String(length=20), nullable=False),
        sa.Column('subtasks_template', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE')
    )
    op.create_index('ix_task_templates_user_id', 'task_templates', ['user_id'])

    # Create template_tags join table
    op.create_table(
        'template_tags',
        sa.Column('template_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tag_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('template_id', 'tag_id'),
        sa.ForeignKeyConstraint(['template_id'], ['task_templates.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], ondelete='CASCADE')
    )
    op.create_index('ix_template_tags_template_id', 'template_tags', ['template_id'])
    op.create_index('ix_template_tags_tag_id', 'template_tags', ['tag_id'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_template_tags_tag_id', table_name='template_tags')
    op.drop_index('ix_template_tags_template_id', table_name='template_tags')
    op.drop_table('template_tags')
    op.drop_index('ix_task_templates_user_id', table_name='task_templates')
    op.drop_table('task_templates')
