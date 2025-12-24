# MCP Architecture Documentation

## Overview

This document describes the Model Context Protocol (MCP) architecture for the Todoly task management application. The system integrates ChatKit (React frontend), OpenAI Agents SDK, FastMCP server, and PostgreSQL database.

---

## 🏗️ High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React + ChatKit)                │
│                  http://localhost:3000                       │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/SSE
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              FastAPI Backend (ChatKit Server)                │
│                  http://localhost:8001                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │         TodolyChatKitServer                          │   │
│  │  - Handles chat requests                             │   │
│  │  - Manages threads & conversations                   │   │
│  │  - Stores chat history in PostgreSQL                 │   │
│  └──────────────┬───────────────────────────────────────┘   │
│                 │                                            │
│                 │ Creates per request                        │
│                 ▼                                            │
│  ┌──────────────────────────────────────────────────────┐   │
│  │         TaskBot Agent (OpenAI Agents SDK)            │   │
│  │  - Agent name: "TaskBot"                             │   │
│  │  - Model: Gemini 2.5 Flash Lite (via LiteLLM)       │   │
│  │  - Instructions: Task management assistant           │   │
│  │  - Connected to: MCP Server (via MCPServerStreamableHttp)│
│  └──────────────┬───────────────────────────────────────┘   │
│                 │                                            │
│                 │ HTTP calls with Bearer token               │
│                 ▼                                            │
└─────────────────────────────────────────────────────────────┘
                         │
                         │ http://localhost:8000/mcp
                         ▼
┌─────────────────────────────────────────────────────────────┐
│           MCP Server (FastMCP + Streamable HTTP)            │
│                  http://localhost:8000/mcp                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │         FastMCP Server Instance                      │   │
│  │  - Name: "Task Management Server"                    │   │
│  │  - Transport: streamable-http                        │   │
│  │  - json_response: True (for scalability)             │   │
│  └──────────────┬───────────────────────────────────────┘   │
│                 │                                            │
│                 │ Exposes MCP Tools                          │
│                 ▼                                            │
│  ┌──────────────────────────────────────────────────────┐   │
│  │         MCP Tools (task_tools.py)                    │   │
│  │  ✅ add_task(title, description, due_date, ...)      │   │
│  │  📋 list_tasks(status, priority, tags, ...)          │   │
│  │  ✏️  update_task(task_id, updates, ...)             │   │
│  │  ❌ delete_task(task_id, ...)                        │   │
│  │  ✅ complete_task(task_id, ...)                      │   │
│  └──────────────┬───────────────────────────────────────┘   │
│                 │                                            │
│                 │ Uses services                              │
│                 ▼                                            │
│  ┌──────────────────────────────────────────────────────┐   │
│  │    Services Layer (TaskService, TagService)          │   │
│  │  - Business logic                                    │   │
│  │  - Validation                                        │   │
│  │  - Database operations via SQLAlchemy ORM            │   │
│  └──────────────┬───────────────────────────────────────┘   │
└─────────────────┼────────────────────────────────────────────┘
                  │
                  │ SQLAlchemy AsyncSession
                  ▼
┌─────────────────────────────────────────────────────────────┐
│         PostgreSQL Database (Neon Cloud)                    │
│  Tables:                                                     │
│  - tasks                                                     │
│  - tags                                                      │
│  - task_tags (many-to-many)                                 │
│  - conversations (ChatKit)                                   │
│  - messages (ChatKit)                                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 Request Flow

### Example: User says "Add a task to buy groceries tomorrow"

#### Step-by-Step Execution:

```
1. Frontend (React)
   └─> User types message in chat
   └─> POST /api/chatkit/chat

2. FastAPI Backend (ChatKit Server)
   └─> TodolyChatKitServer.respond()
   └─> Creates AgentContext with thread + store
   └─> Converts user message to agent input

3. TaskBot Agent (OpenAI Agents SDK)
   └─> Runner.run_streamed(agent, input)
   └─> Agent decides: "I need to use add_task tool"
   └─> Calls MCP Server via MCPServerStreamableHttp

4. MCP Server (FastMCP)
   └─> Receives HTTP request at http://localhost:8000/mcp
   └─> Routes to @mcp.tool() -> add_task()

5. MCP Tool (add_task)
   └─> Parses natural language date ("tomorrow")
   └─> Validates title, priority
   └─> Creates database session
   └─> Calls TaskService.create_task()

6. TaskService
   └─> Validates input
   └─> Creates Task model
   └─> Saves to PostgreSQL via SQLAlchemy
   └─> Returns Task object

7. MCP Tool Response
   └─> Returns JSON: {success: true, task: {...}}

8. TaskBot Agent
   └─> Receives tool result
   └─> Formats friendly response: "✅ I've added 'Buy groceries' to your task list for tomorrow!"

9. FastAPI Backend
   └─> Streams response events to frontend
   └─> Saves conversation to PostgreSQL

10. Frontend
    └─> Displays agent response in chat
    └─> Updates UI
```

---

## 📦 Component Details

### 1. MCP Server

**Location:** `backend/src/mcp_server/server.py`

**Purpose:** Standalone FastMCP server that exposes task management operations as tools

**Configuration:**
```python
mcp = FastMCP(
    "Task Management Server",
    json_response=True,      # Stateless, scalable
    lifespan=lifespan,       # Database lifecycle management
)

# Runs on port 8000
mcp.run(
    transport="streamable-http",
    host="0.0.0.0",
    port=8000,
)
```

**Key Features:**
- ✅ Lifespan management for database connections
- ✅ PostgreSQL connection pooling
- ✅ Async SQLAlchemy sessions
- ✅ Runs independently from FastAPI backend
- ✅ Stateless design for horizontal scaling

**Endpoint:** `http://localhost:8000/mcp`

---

### 2. MCP Tools

**Location:** `backend/src/mcp_server/tools/task_tools.py`

**Purpose:** AI-callable functions that perform task operations

#### Available Tools:

##### `add_task`
```python
@mcp.tool()
async def add_task(
    title: str,
    description: str | None = None,
    due_date: str | None = None,
    priority: str = "medium",
    tags: list[str] | None = None,
    user_id: str = "default_user",
    ctx: Context | None = None,
) -> dict[str, Any]
```

**Capabilities:**
- Natural language date parsing (e.g., "tomorrow", "next Friday")
- Priority validation (low/medium/high)
- Automatic tag creation and association
- Returns structured task data

**Example Usage:**
```
User: "Add a high priority task to finish the report by Friday with tags work, urgent"

Agent calls:
add_task(
    title="Finish the report",
    due_date="Friday",
    priority="high",
    tags=["work", "urgent"]
)

Returns:
{
    "success": true,
    "task": {
        "id": "uuid-here",
        "title": "Finish the report",
        "status": "pending",
        "priority": "high",
        "due_date": "2024-12-27T00:00:00",
        "tags": ["work", "urgent"]
    },
    "message": "✅ Task 'Finish the report' created successfully"
}
```

##### `list_tasks`
```python
@mcp.tool()
async def list_tasks(
    status: str | None = None,
    priority: str | None = None,
    tags: list[str] | None = None,
    user_id: str = "default_user",
    ctx: Context | None = None,
) -> dict[str, Any]
```

**Capabilities:**
- Filter by status (pending/completed)
- Filter by priority (low/medium/high)
- Filter by tags (matches ANY tag)
- Returns list of matching tasks

**Example Usage:**
```
User: "Show me my high priority pending tasks"

Agent calls:
list_tasks(status="pending", priority="high")

Returns:
{
    "success": true,
    "tasks": [
        {
            "id": "uuid-1",
            "title": "Finish the report",
            "status": "pending",
            "priority": "high",
            ...
        }
    ],
    "count": 1,
    "message": "Found 1 task(s)"
}
```

#### Tool Architecture:

```
MCP Tool Function
    ↓
Validates inputs
    ↓
Creates database session
    ↓
Calls Service Layer (TaskService)
    ↓
Service performs business logic
    ↓
Database operations via SQLAlchemy
    ↓
Returns structured response
```

---

### 3. TaskBot Agent

**Location:** `backend/src/core/chatkit_server.py`

**Purpose:** AI agent that understands natural language and calls MCP tools

**Configuration:**
```python
agent = Agent(
    name="TaskBot",
    instructions="""You are a helpful task management assistant...""",
    model=LitellmModel(
        model="gemini/gemini-2.5-flash-lite",
        api_key=settings.GEMINI_API_KEY,
    ),
    model_settings=ModelSettings(
        include_usage=True,
        temperature=0.7,
        max_tokens=2048,
    ),
    mcp_servers=[mcp_server],  # Connected to MCP!
)
```

**Key Features:**
- ✅ Uses Gemini 2.5 Flash Lite (fast & cost-effective)
- ✅ Connected to MCP server via MCPServerStreamableHttp
- ✅ Has access to all MCP tools
- ✅ Streams responses back to frontend
- ✅ Maintains conversation context

**Decision Flow:**
```
User Input
    ↓
Agent analyzes intent
    ↓
Decides which tool to use (if any)
    ↓
Calls MCP tool via HTTP
    ↓
Receives tool result
    ↓
Formats friendly response
    ↓
Streams to frontend
```

---

### 4. MCP Client Connection

**Location:** `backend/src/core/chatkit_server.py` (to be implemented)

**Purpose:** Connects TaskBot agent to MCP server

**Implementation:**
```python
async def _create_agent_with_mcp(self) -> tuple[Agent, MCPServerStreamableHttp]:
    """Create and configure the agent with FastMCP server."""

    # Get token from environment
    token = settings.MCP_SERVER_TOKEN

    # Create MCP client connection
    mcp_server = MCPServerStreamableHttp(
        name="Task Management Server",
        params={
            "url": "http://localhost:8000/mcp",
            "headers": {"Authorization": f"Bearer {token}"},
            "timeout": 10,
        },
        cache_tools_list=True,      # Cache tools for performance
        max_retry_attempts=3,        # Retry on failure
    )

    # Create agent with MCP server
    agent = Agent(
        name="TaskBot",
        instructions="...",
        model=LitellmModel("gemini/gemini-2.5-flash-lite"),
        mcp_servers=[mcp_server],   # Connect to MCP
    )

    return agent, mcp_server
```

**Features:**
- ✅ Bearer token authentication
- ✅ Tool list caching for performance
- ✅ Automatic retry on failures
- ✅ Configurable timeout

---

### 5. Services Layer

**Location:** `backend/src/services/`

**Purpose:** Business logic and database operations

#### TaskService (`task_service.py`)

**Key Methods:**
- `create_task(task_data, user_id)` - Create new task
- `get_tasks(user_id)` - Retrieve user's tasks
- `update_task(task_id, updates, user_id)` - Update task
- `delete_task(task_id, user_id)` - Soft delete task
- `add_tag_to_task(task_id, tag_id, user_id)` - Associate tag

**Architecture:**
```python
class TaskService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_task(
        self,
        task_data: TaskCreate,
        user_id: str
    ) -> Task:
        # Validate
        # Create model
        # Save to database
        # Return task
```

#### TagService (`tag_service.py`)

**Key Methods:**
- `create_tag(tag_data, user_id)` - Create new tag
- `get_tags(user_id)` - Retrieve user's tags
- `get_or_create_tag(name, user_id)` - Get existing or create new

---

### 6. Database Layer

**Technology:** PostgreSQL (Neon Cloud) + SQLAlchemy ORM

**Tables:**

#### `tasks`
```sql
- id (UUID, PK)
- user_id (VARCHAR)
- title (VARCHAR)
- description (TEXT)
- status (ENUM: pending, completed)
- priority (ENUM: low, medium, high)
- due_date (TIMESTAMP)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)
- completed_at (TIMESTAMP)
- deleted_at (TIMESTAMP)
```

#### `tags`
```sql
- id (UUID, PK)
- user_id (VARCHAR)
- name (VARCHAR)
- color (VARCHAR)
- created_at (TIMESTAMP)
```

#### `task_tags` (many-to-many)
```sql
- task_id (UUID, FK)
- tag_id (UUID, FK)
```

#### ChatKit Tables
```sql
- conversations
- messages
- threads
```

---

## 🔐 Authentication & Security

### Bearer Token Authentication

**Flow:**
```
Agent → MCP Client
    ↓
    Adds header: Authorization: Bearer {token}
    ↓
HTTP Request → MCP Server
    ↓
    Validates token (future: implement validation)
    ↓
    Executes tool
    ↓
    Returns result
```

**Configuration:**
```bash
# .env file
MCP_SERVER_TOKEN=your-secret-token-here
```

**Future Enhancements:**
- Token validation middleware
- Rate limiting
- Request logging
- User context from JWT

---

## 📊 Data Flow

### Complete Flow Diagram

```
User Message
    ↓
Frontend React Component
    ↓
HTTP POST /api/chatkit/chat
    ↓
FastAPI Endpoint
    ↓
ChatKit Server (respond method)
    ↓
Agent Input Conversion
    ↓
Runner.run_streamed(agent, input)
    ↓
Agent Prompt Processing
    ↓
Tool Selection (add_task)
    ↓
MCP Client HTTP Request
    ↓
Authorization: Bearer {token}
    ↓
POST http://localhost:8000/mcp
    ↓
FastMCP Server Routing
    ↓
Tool Function Execution
    ↓
Service Layer (TaskService)
    ↓
Business Logic + Validation
    ↓
SQLAlchemy Query
    ↓
PostgreSQL Database Write
    ↓
Task Object Return
    ↓
Tool Result (JSON)
    ↓
MCP HTTP Response
    ↓
Agent Processing
    ↓
Response Formatting
    ↓
Streamed Events (SSE)
    ↓
Frontend Update
    ↓
User Sees Result
```

---

## 🎯 Architecture Benefits

### ✅ Separation of Concerns

**MCP Server (Port 8000):**
- Pure tool exposure
- No chat logic
- Reusable by other clients

**FastAPI Backend (Port 8001):**
- Chat orchestration
- Conversation management
- Agent coordination

**Frontend (Port 3000):**
- UI only
- No business logic
- Clean separation

### ✅ Scalability

**Stateless Design:**
- MCP server uses `json_response=True`
- No session state
- Can scale horizontally

**Connection Pooling:**
- PostgreSQL connection pooling
- Async database operations
- Efficient resource usage

**Caching:**
- Tool list caching in MCP client
- Reduces redundant tool discovery

### ✅ Flexibility

**Multiple Clients:**
- Any agent can connect to MCP server
- Not limited to TaskBot
- CLI tools, other apps can use same MCP server

**Easy Extension:**
- Add new tools: Just decorate function with `@mcp.tool()`
- Add new agents: Create new Agent instances
- Add new models: Swap LitellmModel provider

**Modular Architecture:**
- MCP server runs independently
- Can update tools without restarting chat server
- Can test tools in isolation

### ✅ Security

**Layered Security:**
- Bearer token authentication
- Request validation at multiple layers
- Database connection isolation
- User context separation

**Future Enhancements:**
- JWT-based authentication
- Role-based access control
- Rate limiting per user
- Audit logging

---

## 🔧 Implementation Checklist

### Already Implemented ✅

- [x] MCP Server structure (`src/mcp_server/server.py`)
- [x] Database lifecycle management
- [x] MCP Tools (`add_task`, `list_tasks`)
- [x] Service layer (TaskService, TagService)
- [x] Database models and migrations
- [x] ChatKit server integration
- [x] Frontend React components

### To Implement 🔨

- [ ] Uncomment tools import in `server.py`
- [ ] Add MCPServerStreamableHttp in `chatkit_server.py`
- [ ] Update `_create_agent_with_mcp()` method
- [ ] Add environment variables (MCP_SERVER_TOKEN, MCP_SERVER_URL)
- [ ] Add token validation middleware (optional)
- [ ] Add additional tools (update_task, delete_task, complete_task)
- [ ] Add rate limiting (optional)
- [ ] Add request logging (optional)

---

## 📋 Configuration

### Environment Variables

**Required:**
```bash
# Database
DATABASE_URL=postgresql://user:pass@host/dbname

# LLM Provider
GEMINI_API_KEY=your-gemini-api-key

# MCP Configuration
MCP_SERVER_URL=http://localhost:8000/mcp
MCP_SERVER_TOKEN=your-secret-token-here
```

**Optional:**
```bash
# MCP Server Port
MCP_SERVER_PORT=8000

# Enable debug logging
DEBUG=true

# Rate limiting
MCP_RATE_LIMIT=100
```

### Docker Compose Configuration

```yaml
version: '3.8'

services:
  mcp-server:
    build: ./backend
    command: python -m src.mcp_server.server
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - MCP_SERVER_TOKEN=${MCP_SERVER_TOKEN}

  backend:
    build: ./backend
    command: uvicorn src.main:app --host 0.0.0.0 --port 8001
    ports:
      - "8001:8001"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - MCP_SERVER_URL=http://mcp-server:8000/mcp
      - MCP_SERVER_TOKEN=${MCP_SERVER_TOKEN}
    depends_on:
      - mcp-server

  frontend:
    build: ./frontend
    command: npm run dev
    ports:
      - "3000:3000"
    depends_on:
      - backend
```

---

## 🚀 Startup Sequence

### Development Mode

**Terminal 1: Start MCP Server**
```bash
cd backend
source .venv/bin/activate
python -m src.mcp_server.server

# Expected output:
# ✅ Loaded environment from /path/to/.env
# 🚀 Starting MCP server on http://0.0.0.0:8000/mcp
# 📊 Registered tools: 2 tools
```

**Terminal 2: Start FastAPI Backend**
```bash
cd backend
source .venv/bin/activate
uvicorn src.main:app --reload --port 8001

# Expected output:
# INFO:     Uvicorn running on http://0.0.0.0:8001
# INFO:     Application startup complete.
```

**Terminal 3: Start Frontend**
```bash
cd frontend
npm run dev

# Expected output:
# VITE v5.x ready in 500 ms
# ➜  Local:   http://localhost:3000/
```

### Production Mode

```bash
# Using Docker Compose
docker-compose up -d

# Or using systemd services
sudo systemctl start mcp-server
sudo systemctl start todoly-backend
sudo systemctl start todoly-frontend
```

---

## 🧪 Testing

### Test MCP Server Standalone

```bash
# Test tool discovery
curl http://localhost:8000/mcp/tools

# Test add_task tool
curl -X POST http://localhost:8000/mcp/tools/add_task \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token" \
  -d '{
    "title": "Test task",
    "priority": "high"
  }'
```

### Test Agent Integration

```python
# Run in Python REPL
import asyncio
from agents import Agent, Runner
from agents.mcp import MCPServerStreamableHttp

async def test_agent():
    mcp_server = MCPServerStreamableHttp(
        name="Task Management Server",
        params={
            "url": "http://localhost:8000/mcp",
            "headers": {"Authorization": "Bearer your-token"},
        },
    )

    agent = Agent(
        name="Test Agent",
        instructions="You are a task assistant.",
        mcp_servers=[mcp_server],
    )

    result = await Runner.run(
        agent,
        "Add a task to buy groceries tomorrow"
    )
    print(result.final_output)

asyncio.run(test_agent())
```

---

## 📈 Monitoring & Observability

### Logging

**MCP Server Logs:**
```python
# backend/src/core/logging.py
logger = get_logger(__name__)
logger.info("Tool invoked: add_task")
logger.error("Database error", exc_info=True)
```

**Request Logging:**
```python
# Log all tool invocations
log_tool_invocation(
    tool_name="add_task",
    args={"title": "Test"},
    result={"success": True}
)
```

### Metrics

**Key Metrics to Track:**
- Tool invocation count by type
- Average response time per tool
- Error rate by tool
- Database query performance
- Agent response time
- Token usage per request

---

## 🔍 Troubleshooting

### Common Issues

#### MCP Server Not Starting
```bash
# Check port availability
lsof -i :8000

# Check database connection
psql $DATABASE_URL

# Check environment variables
env | grep MCP
```

#### Agent Cannot Connect to MCP Server
```bash
# Verify MCP server is running
curl http://localhost:8000/mcp

# Check authorization header
curl -H "Authorization: Bearer wrong-token" http://localhost:8000/mcp
```

#### Tools Not Registered
```bash
# Verify tools import is uncommented
cat backend/src/mcp_server/server.py | grep "from src.mcp_server.tools"

# Check tool registration
python -c "from src.mcp_server.server import mcp; print(len(mcp._tools))"
```

---

## 📚 References

- [Model Context Protocol Specification](https://spec.modelcontextprotocol.io/)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [OpenAI Agents SDK](https://github.com/openai/swarm)
- [ChatKit Documentation](https://github.com/chatkit/chatkit)
- [SQLAlchemy Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)

---

## 🤝 Contributing

When adding new MCP tools:

1. Add tool function in `src/mcp_server/tools/task_tools.py`
2. Decorate with `@mcp.tool()`
3. Document parameters and return type
4. Add error handling
5. Add logging
6. Update this documentation
7. Add tests

Example:
```python
@mcp.tool()
async def update_task(
    task_id: str,
    updates: dict[str, Any],
    user_id: str = "default_user",
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Update an existing task.

    Args:
        task_id: Task ID to update
        updates: Dictionary of fields to update
        user_id: User ID
        ctx: FastMCP context

    Returns:
        Updated task data
    """
    # Implementation here
```

---

## 📝 License

This architecture is part of the Todoly project, which is proprietary software developed for the hackathon.

---

**Last Updated:** 2024-12-24
**Version:** 1.0.0
**Author:** Todoly Team
