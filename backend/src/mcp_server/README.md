# TodoMore MCP Server

FastMCP server for exposing task management tools via Model Context Protocol (MCP).

## Overview

This MCP server exposes task management operations as tools that can be invoked by AI agents through the **Streamable HTTP** transport. It integrates with:

- **FastMCP**: For MCP protocol implementation
- **PostgreSQL/Neon**: For task persistence
- **SQLModel**: For ORM
- **Task Service Layer**: For business logic

## Architecture

```
mcp_server/
├── server.py              # Main MCP server with database lifecycle
├── tools/
│   ├── __init__.py
│   └── task_tools.py      # Task management tools (@mcp.tool() decorated)
└── README.md
```

## Available Tools

### `add_task`
Create a new task with natural language date parsing.

**Parameters:**
- `title` (required): Task title (1-100 characters)
- `description` (optional): Task description (max 500 characters)
- `due_date` (optional): Due date in natural language (e.g., "tomorrow", "next Friday")
- `priority` (optional): "low", "medium", or "high" (default: "medium")
- `tags` (optional): List of tag names
- `user_id` (required): User ID for ownership

**Example:**
```json
{
  "title": "Buy groceries",
  "due_date": "tomorrow",
  "priority": "high",
  "tags": ["personal", "shopping"]
}
```

### `list_tasks`
List tasks with optional filtering.

**Parameters:**
- `status` (optional): "pending" or "completed"
- `priority` (optional): "low", "medium", or "high"
- `tags` (optional): Filter by tag names (returns tasks with ANY of these tags)
- `user_id` (required): User ID for filtering

**Example:**
```json
{
  "status": "pending",
  "priority": "high"
}
```

## Running the Server

### Method 1: Using Python directly

```bash
# From backend directory
cd backend

# Set environment variables
export DATABASE_URL="postgresql+asyncpg://user:pass@host/db"

# Run the server
python -m src.mcp_server.server
```

The server will start on `http://0.0.0.0:8001/mcp`

### Method 2: Using uv (recommended)

```bash
# Install mcp package
uv pip install mcp

# Run with uv
uv run --with mcp python -m src.mcp_server.server
```

### Method 3: As a separate service (production)

```bash
# Using uvicorn for production
uvicorn src.mcp_server.server:mcp --host 0.0.0.0 --port 8001
```

## Testing the Server

### Using MCP Inspector

The MCP Inspector is a visual tool for testing MCP servers:

```bash
# Start the MCP server first
python -m src.mcp_server.server

# In another terminal, open inspector
npx -y @modelcontextprotocol/inspector
```

Then connect to: `http://localhost:8001/mcp`

### Using curl

```bash
# List available tools
curl http://localhost:8001/mcp/tools

# Call add_task tool
curl -X POST http://localhost:8001/mcp/call \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "add_task",
    "arguments": {
      "title": "Test task",
      "due_date": "tomorrow",
      "priority": "high",
      "user_id": "test-user-123"
    }
  }'
```

## Connecting from OpenAI Agents SDK

Use `MCPServerStreamableHttp` to connect:

```python
from agents import Agent, Runner
from agents.mcp import MCPServerStreamableHttp
from agents.model_settings import ModelSettings

async def create_agent():
    # Connect to MCP server
    mcp_server = MCPServerStreamableHttp(
        name="Task Management Server",
        params={
            "url": "http://localhost:8001/mcp",
            "headers": {
                "Authorization": "Bearer your-token",
                "X-User-ID": "user-123"
            },
            "timeout": 30,
        },
        cache_tools_list=True,
        max_retry_attempts=3,
    )

    # Create agent with MCP tools
    agent = Agent(
        name="TodoBot",
        instructions="You are a task management assistant.",
        mcp_servers=[mcp_server],
        model_settings=ModelSettings(tool_choice="auto"),
    )

    return agent

# Use the agent
agent = await create_agent()
result = await Runner.run(agent, "Add a task to buy milk tomorrow")
print(result.final_output)
```

## Environment Variables

Required:
- `DATABASE_URL`: PostgreSQL connection string (automatically converted to asyncpg format)

Optional:
- `MCP_SERVER_TOKEN`: Authentication token for MCP clients (recommended for production)

## Database Schema

The server uses your existing database schema with tables:
- `tasks`: Main task storage
- `users`: User accounts
- `tags`: Tag definitions
- `task_tags`: Task-tag relationships

## Logging

The server logs all tool invocations using `src.core.logging.log_tool_invocation()`.

View logs:
```bash
tail -f logs/mcp_server.log
```

## Security Considerations

1. **Authentication**: Implement token-based auth via `MCP_SERVER_TOKEN`
2. **User Isolation**: Always validate `user_id` from headers/context
3. **Input Validation**: All inputs are validated by Pydantic models
4. **SQL Injection**: Protected by SQLAlchemy ORM

## Troubleshooting

### Port already in use
```bash
# Find process using port 8001
lsof -i :8001

# Kill the process
kill -9 <PID>
```

### Database connection errors
- Verify `DATABASE_URL` is set correctly
- Ensure PostgreSQL is running
- Check network connectivity to database

### Tools not showing up
- Verify `src/mcp_server/tools/task_tools.py` imports correctly
- Check that `@mcp.tool()` decorator is present
- Restart the server

## Development

### Adding new tools

1. Add tool function to `tools/task_tools.py`:

```python
@mcp.tool()
async def my_new_tool(
    param: str,
    user_id: str = "default_user",
    ctx: Context = CurrentContext(),
) -> dict[str, Any]:
    """Tool description for AI agent."""
    # Implementation
    return {"success": True, "data": result}
```

2. Restart the server
3. Tool will automatically be available to agents

### Running tests

```bash
pytest tests/test_mcp_tools.py -v
```

## Resources

- [MCP Documentation](https://modelcontextprotocol.io/)
- [FastMCP GitHub](https://github.com/jlowin/fastmcp)
- [OpenAI Agents SDK](https://github.com/openai/openai-agents-python)
