
import asyncio
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from src.config import settings

logger = logging.getLogger(__name__)


class DatabaseSessionManager:
    def __init__(self, host: str, engine_kwargs: dict = {}):
        self._engine = create_async_engine(host, **engine_kwargs)
        self._sessionmaker = async_sessionmaker(
            bind=self._engine, expire_on_commit=False, class_=AsyncSession
        )

    async def close(self):
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")
        await self._engine.dispose()

        self._engine = None
        self._sessionmaker = None

    @asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")

        retries = 5 if settings.ENVIRONMENT == "production" else 0
        last_exception = None

        for attempt in range(retries + 1):
            try:
                async with self._engine.begin() as connection:
                    yield connection
                return
            except Exception as e:
                last_exception = e
                if attempt < retries:
                    wait_time = 2**attempt
                    logger.warning(
                        f"Database connection attempt {attempt + 1} failed. "
                        f"Retrying in {wait_time}s... Error: {e}"
                    )
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"All {retries + 1} database connection attempts failed.")
        
        if last_exception:
            raise last_exception

    @asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        if self._sessionmaker is None:
            raise Exception("DatabaseSessionManager is not initialized")

        session = self._sessionmaker()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def _get_engine_kwargs() -> dict:
    """Get engine kwargs based on database URL and environment."""
    # SQLite doesn't support connection pooling
    if settings.DATABASE_URL.startswith("sqlite"):
        return {"echo": settings.LOG_LEVEL == "DEBUG"}

    # Serverless/Vercel-friendly settings
    # - pool_pre_ping: validates connection before use (fixes "connection is closed")
    # - pool_recycle: lower value for serverless (300s instead of 3600s)
    # - pool_size=0: let pool manage connections dynamically
    # - max_overflow=0: no overflow connections in serverless
    return {
        "pool_size": 0,
        "max_overflow": 0,
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "echo": settings.LOG_LEVEL == "DEBUG",
    }


session_manager = DatabaseSessionManager(
    settings.DATABASE_URL,
    engine_kwargs=_get_engine_kwargs(),
)


async def get_db() -> AsyncIterator[AsyncSession]:
    async with session_manager.session() as session:
        yield session
