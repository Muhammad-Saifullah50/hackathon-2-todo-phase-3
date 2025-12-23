"""add_better_auth_tables

Revision ID: a9aa138e5efb
Revises: 805af8b6195e
Create Date: 2025-12-22 10:34:02.062781

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a9aa138e5efb'
down_revision: Union[str, Sequence[str], None] = '805af8b6195e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create Better Auth tables with snake_case column names."""

    # Create session table
    op.create_table(
        'session',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('expires_at', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('token', sa.String(), nullable=False, unique=True),
        sa.Column('ip_address', sa.String(), nullable=True),
        sa.Column('user_agent', sa.String(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_session_user_id', 'session', ['user_id'])
    op.create_index('idx_session_token', 'session', ['token'])

    # Create verification table
    op.create_table(
        'verification',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('identifier', sa.String(), nullable=False),
        sa.Column('value', sa.String(), nullable=False),
        sa.Column('expires_at', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('idx_verification_identifier', 'verification', ['identifier'])

    # Create account table (for OAuth providers)
    op.create_table(
        'account',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('account_id', sa.String(), nullable=False),
        sa.Column('provider_id', sa.String(), nullable=False),
        sa.Column('access_token', sa.Text(), nullable=True),
        sa.Column('refresh_token', sa.Text(), nullable=True),
        sa.Column('id_token', sa.Text(), nullable=True),
        sa.Column('access_token_expires_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('refresh_token_expires_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('scope', sa.String(), nullable=True),
        sa.Column('password', sa.String(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_account_user_id', 'account', ['user_id'])

    # Create triggers for updated_at columns
    op.execute("""
        CREATE TRIGGER update_session_updated_at BEFORE UPDATE ON session
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    """)

    op.execute("""
        CREATE TRIGGER update_verification_updated_at BEFORE UPDATE ON verification
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    """)

    op.execute("""
        CREATE TRIGGER update_account_updated_at BEFORE UPDATE ON account
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    """)


def downgrade() -> None:
    """Drop Better Auth tables."""
    # Drop triggers first
    op.execute('DROP TRIGGER IF EXISTS update_account_updated_at ON account;')
    op.execute('DROP TRIGGER IF EXISTS update_verification_updated_at ON verification;')
    op.execute('DROP TRIGGER IF EXISTS update_session_updated_at ON session;')

    # Drop tables
    op.drop_table('account')
    op.drop_table('verification')
    op.drop_table('session')
