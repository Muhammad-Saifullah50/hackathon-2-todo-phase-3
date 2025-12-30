"""Database connection module for MCP server.

This module provides database session management for MCP tools.
"""

import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Load environment variables
env_path = Path(__file__).parent.parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# Create engine and session factory at module load time
# This ensures the database is always ready when tools are invoked
_db_engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
) if DATABASE_URL else None

_db_session_factory = sessionmaker(
    _db_engine,
    class_=AsyncSession,
    expire_on_commit=False,
) if _db_engine else None


async def connect_db():
    """Initialize database connection (legacy - now auto-connects)."""
    global _db_engine, _db_session_factory
    if _db_engine is None and DATABASE_URL:
        _db_engine = create_async_engine(
            DATABASE_URL,
            echo=False,
            pool_pre_ping=True,
        )
        _db_session_factory = sessionmaker(
            _db_engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )


async def disconnect_db():
    """Close database connection."""
    global _db_engine, _db_session_factory
    if _db_engine:
        await _db_engine.dispose()
        _db_engine = None
        _db_session_factory = None


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get a database session as an async context manager.

    Usage:
        async with get_session() as session:
            # use session
    """
    if not _db_session_factory:
        raise RuntimeError("Database not connected. DATABASE_URL may not be set.")

    session = _db_session_factory()
    try:
        yield session
    finally:
        await session.close()
