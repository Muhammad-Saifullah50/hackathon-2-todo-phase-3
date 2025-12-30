"""FastMCP server for task management tools.

This module sets up the MCP (Model Context Protocol) server that exposes
task management operations as tools that can be invoked by AI agents.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from .env file
# Look for .env in backend directory (parent of src)
env_path = Path(__file__).parent.parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)
    print(f"✅ Loaded environment from {env_path}")
else:
    print(f"⚠️  .env file not found at {env_path}, using system environment variables")

# Get database URL from environment (for validation only)
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set")

# Import mcp instance from the dedicated module
from src.mcp_server.mcp_instance import mcp  # noqa: E402

# Import tools to register them with the MCP server
# This import triggers the @mcp.tool() decorators
from src.mcp_server.tools import task_tools  # noqa: E402, F401

if __name__ == "__main__":
    # Run with Streamable HTTP transport using FastMCP's built-in runner
    # This is the correct way according to MCP SDK documentation
    print(f"🚀 Starting MCP Server on http://{mcp.settings.host}:{mcp.settings.port}")

    # Use mcp.run() with transport="streamable-http"
    # This properly initializes the server and exposes tools via HTTP
    mcp.run(transport="streamable-http")
