"""add_trigram_indexes

Revision ID: 2f4a8c1b9d0e
Revises: 543871da331e
Create Date: 2026-07-05 12:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "2f4a8c1b9d0e"
down_revision: Union[str, Sequence[str], None] = "543871da331e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add pg_trgm extension and trigram indexes for fast ILIKE search on tasks."""
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    op.create_index(
        "idx_tasks_title_trgm",
        "tasks",
        ["title"],
        postgresql_using="gin",
        postgresql_ops={"title": "gin_trgm_ops"},
        if_not_exists=True,
    )
    op.create_index(
        "idx_tasks_description_trgm",
        "tasks",
        ["description"],
        postgresql_using="gin",
        postgresql_ops={"description": "gin_trgm_ops"},
        if_not_exists=True,
    )


def downgrade() -> None:
    op.drop_index("idx_tasks_description_trgm", table_name="tasks", if_exists=True)
    op.drop_index("idx_tasks_title_trgm", table_name="tasks", if_exists=True)
