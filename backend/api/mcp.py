"""Vercel-compatible MCP server entry point.

This module provides a Vercel-compatible ASGI app for the MCP server
using Streamable HTTP transport. Designed to work with Vercel's
serverless Python runtime.
"""

import os
from pathlib import Path
from typing import AsyncGenerator

from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

# Validate environment
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set")

# Import MCP instance and tools (this registers the tools)
from src.mcp_server.mcp_instance import mcp
from src.mcp_server.tools import task_tools  # noqa: F401


async def handle_mcp(scope, receive, send):
    """Handle MCP requests for Vercel serverless environment."""
    await mcp.streamable_http_app()(scope, receive, send)


# Vercel entry point - exports the ASGI app
app = mcp.streamable_http_app()
