"""FastMCP server for task management tools.

This module sets up the MCP (Model Context Protocol) server that exposes
task management operations as tools that can be invoked by AI agents.
"""

import os
from contextlib import asynccontextmanager

from mcp.server.fastmcp import FastMCP
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set")

# Convert postgresql:// to postgresql+asyncpg:// for async support
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")


# Database connection manager
class Database:
    """Database connection manager for MCP server."""

    def __init__(self):
        self.engine = None
        self.session_factory = None

    async def connect(self):
        """Initialize database connection."""
        self.engine = create_async_engine(
            DATABASE_URL,
            echo=False,
            pool_pre_ping=True,
        )
        self.session_factory = sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    async def disconnect(self):
        """Close database connection."""
        if self.engine:
            await self.engine.dispose()

    def get_session(self) -> AsyncSession:
        """Get a new database session."""
        if not self.session_factory:
            raise RuntimeError("Database not connected")
        return self.session_factory()


# Create database instance
db = Database()


@asynccontextmanager
async def lifespan():
    """Manage database lifecycle."""
    await db.connect()
    yield
    await db.disconnect()


# Create MCP server with lifespan
mcp = FastMCP(
    "Task Management Server",
    json_response=True,
    lifespan=lifespan,
)

# Import tools to register them with the MCP server
# This must be after mcp is created so tools can import it
from src.mcp_server.tools import task_tools  # noqa: E402, F401

if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=8001,  # Different port from main API
    )
