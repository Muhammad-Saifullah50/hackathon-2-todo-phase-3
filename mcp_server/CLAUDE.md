# TodoMore MCP Server - Development Guidelines

This file contains project-specific guidelines for Claude Code when working on the TodoMore MCP (Model Context Protocol) server.

## Project Overview

**TodoMore MCP Server** - A FastMCP-based server that exposes task management tools via the Model Context Protocol, enabling AI assistants to interact with the TodoMore backend database directly. Designed for serverless deployment on Vercel.

**Tech Stack:**
- Python 3.13+
- FastAPI 0.100+ for HTTP framework
- FastMCP 2.0+ for MCP protocol implementation
- asyncpg for PostgreSQL async database access
- Neon PostgreSQL 16+ for database (serverless)
- python-dateutil for date parsing
- Vercel for serverless deployment

**Architecture:**
- FastMCP server with stateless HTTP transport
- Direct database access using asyncpg connection pool
- Serverless-ready with lifespan management
- CORS-enabled for cross-origin AI clients
- Monkey-patched security middleware for Vercel compatibility

## Core Principles

### 1. Code Quality Standards

- **Type Hints:** All function signatures must include type hints (Python 3.10+ style)
- **Async/Await:** Use async functions for all database operations
- **Error Handling:** Return structured error responses with `success: False`
- **Validation:** Validate all inputs before database operations
- **Documentation:** Docstrings for all MCP tools explaining parameters and return values

### 2. MCP Tool Design

- **Tool Names:** Use snake_case (e.g., `add_task`, `list_tasks`)
- **Return Format:** Always return `dict[str, Any]` with `success` boolean and `message` string
- **Error Format:** Return `{"success": False, "error": "error message"}`
- **Success Format:** Return `{"success": True, "data": {...}, "message": "success message"}`
- **User ID:** Always include `user_id` parameter with default `"default_user"`

### 3. Database Operations

- **Connection Pool:** Use the global asyncpg connection pool
- **Transactions:** Use transactions for multi-step operations
- **Soft Deletes:** Always use `deleted_at IS NULL` filters
- **UTC Timezone:** All timestamps in UTC
- **Error Recovery:** Handle database errors gracefully with descriptive messages

### 4. Deployment Considerations

- **Stateless:** No in-memory state between requests
- **Connection Pooling:** Minimal pool size (1-5 connections) for serverless
- **Timeouts:** Short command timeouts (60s) for serverless environments
- **Environment Variables:** All config from environment, never hardcoded
- **CORS:** Allow all origins for Vercel proxy compatibility

## File Organization

### Project Structure

```
mcp_server/
├── main.py              # FastAPI app + FastMCP tools
├── requirements.txt     # Python dependencies
├── vercel.json         # Vercel deployment config
├── .env                # Environment variables (not committed)
└── .venv/              # Virtual environment (not committed)
```

### When Adding New Tools

1. **Define the Tool:**
   - Use `@mcp.tool()` decorator
   - Include type hints for all parameters
   - Add clear docstring

2. **Validate Inputs:**
   - Check required fields
   - Validate enums (status, priority, etc.)
   - Parse dates with proper error handling

3. **Database Operations:**
   - Get connection from pool
   - Use transactions for write operations
   - Handle errors with try/except

4. **Return Structured Response:**
   - Always include `success` boolean
   - Include `message` for user feedback
   - Return relevant data in `task`, `tasks`, or custom key

## MCP Tool Patterns

### Tool Decorator and Type Hints

```python
@mcp.tool()
async def tool_name(
    required_param: str,
    optional_param: str | None = None,
    user_id: str = "default_user",
) -> dict[str, Any]:
    """Brief description of what the tool does.

    Args:
        required_param: Description of parameter
        optional_param: Description of optional parameter
        user_id: User ID for task ownership

    Returns:
        Dictionary with success status, data, and message
    """
    # Implementation
```

### Database Query Pattern

```python
@mcp.tool()
async def get_something(
    filter_param: str | None = None,
    user_id: str = "default_user",
) -> dict[str, Any]:
    """Get something from database."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        try:
            # Build query
            query = """
                SELECT * FROM table_name
                WHERE user_id = $1 AND deleted_at IS NULL
            """
            params = [user_id]

            # Add optional filters
            if filter_param:
                query += " AND column = $2"
                params.append(filter_param)

            # Execute query
            rows = await conn.fetch(query, *params)

            # Process results
            results = [dict(row) for row in rows]

            return {
                "success": True,
                "data": results,
                "count": len(results),
                "message": f"Found {len(results)} item(s)",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
```

### Database Write Pattern (with Transaction)

```python
@mcp.tool()
async def create_something(
    title: str,
    description: str | None = None,
    user_id: str = "default_user",
) -> dict[str, Any]:
    """Create something in database."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            try:
                # Validate inputs
                if not title.strip():
                    return {"success": False, "error": "Title cannot be empty"}

                # Generate ID and timestamp
                item_id = str(uuid.uuid4())
                now = datetime.now(timezone.utc)

                # Insert into database
                await conn.execute(
                    """
                    INSERT INTO table_name (id, user_id, title, description, created_at)
                    VALUES ($1, $2, $3, $4, $5)
                    """,
                    item_id, user_id, title, description, now
                )

                return {
                    "success": True,
                    "item": {
                        "id": item_id,
                        "title": title,
                        "description": description,
                        "created_at": now.isoformat(),
                    },
                    "message": f"✅ Created '{title}' successfully",
                }
            except Exception as e:
                return {"success": False, "error": str(e)}
```

### Date Parsing Pattern

```python
# Parse date with timezone handling
parsed_date = None
if date_string:
    try:
        # Parse with dateutil parser
        parsed_date = parser.parse(date_string)

        # If naive (no timezone), assume UTC
        if parsed_date.tzinfo is None:
            parsed_date = parsed_date.replace(tzinfo=timezone.utc)
        else:
            # Convert to UTC if different timezone
            parsed_date = parsed_date.astimezone(timezone.utc)
    except Exception as e:
        return {"success": False, "error": f"Invalid date format: {str(e)}"}
```

### Enum Validation Pattern

```python
# Validate enum value
if value.lower() not in ["option1", "option2", "option3"]:
    return {
        "success": False,
        "error": f"Invalid value '{value}'. Must be 'option1', 'option2', or 'option3'.",
    }

# Use lowercase for storage
validated_value = value.lower()
```

## Existing MCP Tools

### add_task
Creates a new task with validation and tag support.

**Parameters:**
- `title: str` - Task title (required)
- `description: str | None` - Optional description
- `due_date: str | None` - ISO date string or parseable date
- `priority: str` - "low", "medium", or "high" (default: "medium")
- `tags: list[str] | None` - List of tag names
- `user_id: str` - User ID (default: "default_user")

**Returns:**
```python
{
    "success": True,
    "task": {
        "id": "uuid",
        "title": "Task title",
        "description": "Description",
        "status": "pending",
        "priority": "medium",
        "due_date": "2024-01-01T00:00:00+00:00",
        "created_at": "2024-01-01T00:00:00+00:00",
        "tags": ["tag1", "tag2"],
    },
    "message": "✅ Task 'Task title' created successfully",
}
```

### list_tasks
Lists tasks with optional filters.

**Parameters:**
- `status: str | None` - Filter by status ("pending", "completed")
- `priority: str | None` - Filter by priority ("low", "medium", "high")
- `tags: list[str] | None` - Filter by tags (currently not implemented)
- `user_id: str` - User ID (default: "default_user")

**Returns:**
```python
{
    "success": True,
    "tasks": [
        {
            "id": "uuid",
            "title": "Task title",
            "description": "Description",
            "status": "pending",
            "priority": "medium",
            "due_date": "2024-01-01T00:00:00+00:00",
            "created_at": "2024-01-01T00:00:00+00:00",
            "completed_at": None,
            "tags": ["tag1"],
        }
    ],
    "count": 1,
    "message": "Found 1 task(s)",
}
```

### complete_task
Marks a task as completed.

**Parameters:**
- `task_id: str` - Task ID (required)
- `user_id: str` - User ID (default: "default_user")

**Returns:**
```python
{
    "success": True,
    "task": {
        "id": "uuid",
        "title": "Task title",
        "status": "completed",
        "completed_at": "2024-01-01T00:00:00+00:00",
    },
    "message": "✅ Task 'Task title' marked as complete",
}
```

### update_task
Updates task fields.

**Parameters:**
- `task_id: str` - Task ID (required)
- `title: str | None` - New title
- `description: str | None` - New description
- `priority: str | None` - New priority
- `due_date: str | None` - New due date
- `user_id: str` - User ID (default: "default_user")

**Returns:**
```python
{
    "success": True,
    "task": {
        "id": "uuid",
        "title": "Updated title",
        "description": "Updated description",
        "status": "pending",
        "priority": "high",
        "due_date": "2024-01-01T00:00:00+00:00",
    },
    "message": "✏️ Task 'Updated title' updated",
}
```

### delete_task
Soft deletes a task.

**Parameters:**
- `task_id: str` - Task ID (required)
- `user_id: str` - User ID (default: "default_user")

**Returns:**
```python
{
    "success": True,
    "task": {
        "id": "uuid",
        "title": "Task title",
        "status": "deleted",
    },
    "message": "🗑️ Task 'Task title' deleted",
}
```

## Database Schema

The MCP server directly accesses these tables:

### tasks
```sql
CREATE TABLE tasks (
    id UUID PRIMARY KEY,
    user_id VARCHAR NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    priority VARCHAR(10) NOT NULL DEFAULT 'medium',
    due_date TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    completed_at TIMESTAMPTZ,
    deleted_at TIMESTAMPTZ,
    INDEX idx_user_deleted (user_id, deleted_at)
);
```

### tags
```sql
CREATE TABLE tags (
    id UUID PRIMARY KEY,
    user_id VARCHAR NOT NULL,
    name VARCHAR(50) NOT NULL,
    color VARCHAR(7) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    UNIQUE (user_id, LOWER(name))
);
```

### task_tags
```sql
CREATE TABLE task_tags (
    task_id UUID REFERENCES tasks(id) ON DELETE CASCADE,
    tag_id UUID REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (task_id, tag_id)
);
```

## Common Patterns

### Creating a New MCP Tool

1. **Define tool with decorator:**
```python
@mcp.tool()
async def new_tool_name(
    required_param: str,
    optional_param: str | None = None,
    user_id: str = "default_user",
) -> dict[str, Any]:
    """Clear description of what the tool does."""
```

2. **Get database connection:**
```python
    pool = await get_pool()
    async with pool.acquire() as conn:
```

3. **Validate inputs:**
```python
        if not required_param.strip():
            return {"success": False, "error": "Required param cannot be empty"}
```

4. **Execute database operations:**
```python
        try:
            # For writes, use transaction
            async with conn.transaction():
                result = await conn.execute(query, *params)

            return {
                "success": True,
                "data": result,
                "message": "Operation successful",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
```

## Deployment

### Environment Variables

Required environment variables:

```bash
DATABASE_URL=postgresql+asyncpg://user:pass@host/db
FRONTEND_URL=https://your-frontend.vercel.app  # Optional
```

### Vercel Deployment

1. **Deploy directory as separate Vercel project:**
   ```bash
   cd mcp_server
   vercel
   ```

2. **Configure environment variables in Vercel dashboard:**
   - Add `DATABASE_URL` from Neon/PostgreSQL

3. **Verify deployment:**
   ```bash
   curl https://your-mcp-server.vercel.app/health
   ```

### Testing MCP Endpoints

**Health check:**
```bash
curl https://your-mcp-server.vercel.app/health
```

**MCP SSE endpoint:**
```bash
curl https://your-mcp-server.vercel.app/mcp/sse
```

**List tools:**
```bash
curl -X POST https://your-mcp-server.vercel.app/mcp/message \
  -H "Content-Type: application/json" \
  -d '{"method": "tools/list"}'
```

## Common Mistakes to Avoid

### ❌ Don't Do This

```python
# 1. Hardcoding database URL
DATABASE_URL = "postgresql://localhost/db"  # ❌ Use environment variable

# 2. Not using connection pool
conn = await asyncpg.connect(DATABASE_URL)  # ❌ Creates new connection every time

# 3. Not using transactions for writes
await conn.execute("INSERT ...")  # ❌ No transaction
await conn.execute("UPDATE ...")

# 4. Not handling errors
@mcp.tool()
async def my_tool():
    result = await conn.fetch(query)  # ❌ No error handling
    return result

# 5. Not validating inputs
@mcp.tool()
async def create_task(title: str):
    await conn.execute("INSERT INTO tasks (title) VALUES ($1)", title)  # ❌ No validation
```

### ✅ Do This Instead

```python
# 1. Use environment variables
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL not set")

# 2. Use connection pool
pool = await get_pool()
async with pool.acquire() as conn:
    # Use connection

# 3. Use transactions for writes
async with conn.transaction():
    await conn.execute("INSERT ...")
    await conn.execute("UPDATE ...")

# 4. Handle errors properly
@mcp.tool()
async def my_tool():
    try:
        result = await conn.fetch(query)
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

# 5. Validate inputs
@mcp.tool()
async def create_task(title: str):
    if not title.strip():
        return {"success": False, "error": "Title cannot be empty"}

    await conn.execute("INSERT INTO tasks (title) VALUES ($1)", title.strip())
```

## Vercel-Specific Considerations

### Security Middleware Patch

The MCP SDK's `TransportSecurityMiddleware` validates Host headers and blocks Vercel proxy requests. We monkey-patch it to allow all hosts:

```python
# CRITICAL: Disable DNS rebinding protection for Vercel
from mcp.server.transport_security import TransportSecurityMiddleware

def _patched_validate_host(self, host):
    """Allow all hosts for Vercel deployment"""
    return True

TransportSecurityMiddleware._validate_host = _patched_validate_host
```

### Mounting MCP App

Use the correct FastMCP API:

```python
# ✅ Correct - Use streamable_http_app() method
mcp_app = mcp.streamable_http_app()
app.mount("/mcp", mcp_app)

# ❌ Wrong - streamable_http_path is a configuration parameter, not a method
mcp_app = mcp.streamable_http_path  # This is incorrect
```

### CORS Configuration

Allow all origins to avoid Vercel proxy issues:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Required for Vercel
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Mcp-Session-Id", "Content-Type"],
)
```

## Performance Considerations

- **Connection Pool:** Use minimal pool size (1-5) for serverless
- **Query Limits:** Always limit result sets (e.g., `LIMIT 100`)
- **Indexes:** Ensure database has proper indexes on `user_id` and `deleted_at`
- **Timeouts:** Set reasonable command timeouts (60s) for serverless
- **Cold Starts:** First request may be slower due to connection pool initialization

## Security Considerations

- **SQL Injection:** Always use parameterized queries with `$1`, `$2`, etc.
- **Input Validation:** Validate all user inputs before database operations
- **User Isolation:** Always filter by `user_id` to prevent unauthorized access
- **Soft Deletes:** Always check `deleted_at IS NULL` to exclude deleted records
- **Environment Variables:** Never commit `.env` file or hardcode credentials

## Quick Reference

### Run Locally
```bash
cd mcp_server
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn main:app --reload
```

### Test Endpoints
```bash
# Health check
curl http://localhost:8000/health

# MCP SSE endpoint
curl http://localhost:8000/mcp/sse

# List tools
curl -X POST http://localhost:8000/mcp/message \
  -H "Content-Type: application/json" \
  -d '{"method": "tools/list"}'
```

### Deploy to Vercel
```bash
cd mcp_server
vercel
```

---

**Remember:** The MCP server is designed for serverless deployment with direct database access. Keep tools focused, validate inputs, handle errors gracefully, and always use connection pooling.

## Active Technologies
- Python 3.13+
- FastAPI 0.100+
- FastMCP 2.0+
- asyncpg (PostgreSQL async driver)
- Neon PostgreSQL 16+ (serverless)
- python-dateutil
- Vercel (serverless deployment)

## Recent Changes
- Phase 3: Created MCP server for AI assistant integration
- Added 5 core tools: add_task, list_tasks, complete_task, update_task, delete_task
- Implemented Vercel deployment with security middleware patches
- Added direct database access with asyncpg connection pooling
