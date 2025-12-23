"""Database utilities and health check functions."""

import logging
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import session_manager

logger = logging.getLogger(__name__)


async def check_db_connection() -> bool:
    """
    Check if database connection is healthy.

    Returns:
        True if connection is successful, False otherwise.
    """
    try:
        async with session_manager.connect() as connection:
            await connection.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database connection check failed: {e}")
        return False
