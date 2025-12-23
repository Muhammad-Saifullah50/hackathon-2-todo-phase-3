"""create_template_tags_join_table

Revision ID: 805af8b6195e
Revises: 08923684a9b6
Create Date: 2025-12-22 09:39:18.421902

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '805af8b6195e'
down_revision: Union[str, Sequence[str], None] = '08923684a9b6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'template_tags',
        sa.Column('template_id', sa.String(length=36), nullable=False),
        sa.Column('tag_id', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('template_id', 'tag_id'),
        sa.ForeignKeyConstraint(['template_id'], ['task_templates.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_template_tags_template_id', 'template_tags', ['template_id'])
    op.create_index('ix_template_tags_tag_id', 'template_tags', ['tag_id'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_template_tags_tag_id', table_name='template_tags')
    op.drop_index('ix_template_tags_template_id', table_name='template_tags')
    op.drop_table('template_tags')
