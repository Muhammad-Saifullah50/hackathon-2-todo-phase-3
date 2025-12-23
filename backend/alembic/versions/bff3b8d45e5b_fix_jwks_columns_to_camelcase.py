"""fix_jwks_columns_to_camelcase

Revision ID: bff3b8d45e5b
Revises: 9228e330fc02
Create Date: 2025-12-22 10:43:13.913130

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bff3b8d45e5b'
down_revision: Union[str, Sequence[str], None] = '9228e330fc02'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Rename jwks columns to camelCase for Better Auth compatibility."""
    op.alter_column('jwks', 'public_key', new_column_name='publicKey')
    op.alter_column('jwks', 'private_key', new_column_name='privateKey')
    op.alter_column('jwks', 'created_at', new_column_name='createdAt')


def downgrade() -> None:
    """Revert jwks columns to snake_case."""
    op.alter_column('jwks', 'publicKey', new_column_name='public_key')
    op.alter_column('jwks', 'privateKey', new_column_name='private_key')
    op.alter_column('jwks', 'createdAt', new_column_name='created_at')
