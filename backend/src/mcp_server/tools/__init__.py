"""MCP tools initialization.

Import all tool modules to ensure they're registered with the FastMCP server.
"""

# Import tool modules to register decorators
from . import task_tools  # noqa: F401

__all__ = ["task_tools"]
