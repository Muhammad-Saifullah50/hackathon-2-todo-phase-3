"""add_jwks_table

Revision ID: 9228e330fc02
Revises: a9aa138e5efb
Create Date: 2025-12-22 10:40:25.788570

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9228e330fc02'
down_revision: Union[str, Sequence[str], None] = 'a9aa138e5efb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create jwks table for Better Auth JWT plugin."""
    op.create_table(
        'jwks',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('public_key', sa.Text(), nullable=False),
        sa.Column('private_key', sa.Text(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    """Drop jwks table."""
    op.drop_table('jwks')
