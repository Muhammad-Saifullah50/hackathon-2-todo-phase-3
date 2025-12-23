"""Create tags and task_tags tables

Revision ID: 20251221_124431
Revises: b8404f65f979
Create Date: 2025-12-21

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '20251221_124431'
down_revision: Union[str, Sequence[str], None] = 'b8404f65f979'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create tags and task_tags tables."""
    # Create tags table
    op.create_table(
        'tags',
        sa.Column('id', sa.Uuid(), nullable=False, default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('color', sa.String(length=7), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'name', name='uq_tags_user_id_name'),
        sa.CheckConstraint("char_length(name) >= 1 AND char_length(name) <= 50", name='ck_tags_name_length'),
        sa.CheckConstraint("color ~ '^#[0-9A-Fa-f]{6}$'", name='ck_tags_color_format'),
    )
    op.create_index('ix_tags_user_id', 'tags', ['user_id'])
    op.create_index('ix_tags_user_id_name', 'tags', ['user_id', 'name'])

    # Create task_tags join table
    op.create_table(
        'task_tags',
        sa.Column('task_id', sa.Uuid(), nullable=False),
        sa.Column('tag_id', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('task_id', 'tag_id'),
    )
    op.create_index('ix_task_tags_tag_id', 'task_tags', ['tag_id'])
    op.create_index('ix_task_tags_task_id', 'task_tags', ['task_id'])


def downgrade() -> None:
    """Drop tags and task_tags tables."""
    op.drop_index('ix_task_tags_task_id', table_name='task_tags')
    op.drop_index('ix_task_tags_tag_id', table_name='task_tags')
    op.drop_table('task_tags')
    op.drop_index('ix_tags_user_id_name', table_name='tags')
    op.drop_index('ix_tags_user_id', table_name='tags')
    op.drop_table('tags')
