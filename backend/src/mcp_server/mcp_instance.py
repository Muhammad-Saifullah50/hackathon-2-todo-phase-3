"""MCP server instance.

This module creates the FastMCP instance separately to avoid circular imports.
Tools and other modules should import mcp from here.
"""

from mcp.server.fastmcp import FastMCP

# Create MCP server instance
# This is the single source of truth for the mcp object
mcp = FastMCP(
    "Task Management Server",
    host="0.0.0.0",
    port=8000,
)
