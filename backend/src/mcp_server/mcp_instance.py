"""MCP server instance.

This module creates the FastMCP instance separately to avoid circular imports.
Tools and other modules should import mcp from here.
"""

import os
from mcp.server.fastmcp import FastMCP

# Get MCP server configuration from environment variables
# Defaults are for local development
MCP_HOST = os.getenv("MCP_HOST", "0.0.0.0")
MCP_PORT = int(os.getenv("MCP_PORT", "8000"))

# Create MCP server instance
# This is the single source of truth for the mcp object
mcp = FastMCP(
    "Task Management Server",
    host=MCP_HOST,
    port=MCP_PORT,
)
