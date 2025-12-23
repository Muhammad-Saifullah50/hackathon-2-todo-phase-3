"""Integration tests for database migrations."""

import pytest
from sqlalchemy import Connection, inspect
from sqlalchemy.ext.asyncio import AsyncEngine


@pytest.mark.asyncio
async def test_migration_tables_exist(test_engine: AsyncEngine) -> None:
    """Test that the required tables exist after migrations (init_db in tests)."""
    async with test_engine.connect() as conn:

        def get_table_names(connection: Connection) -> list[str]:
            inspector = inspect(connection)
            return inspector.get_table_names()

        table_names = await conn.run_sync(get_table_names)

        assert "tasks" in table_names
        assert "user" in table_names
