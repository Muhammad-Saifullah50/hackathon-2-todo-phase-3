# Quickstart Guide: AI-Powered Task Management Chatbot

**Date**: 2025-12-23
**Feature**: 007-ai-chatbot

This guide provides step-by-step instructions to set up, run, and test the AI chatbot feature locally.

---

## Prerequisites

### Required Software
- **Python**: 3.13+ (backend)
- **Node.js**: 20+ LTS (frontend)
- **PostgreSQL**: 16+ (database)
- **Docker**: Latest (for local PostgreSQL)
- **Git**: Version control

### Required API Keys
- **Zhipu AI API Key**: For GLM-4.5-air model
  - Sign up at [https://open.bigmodel.cn](https://open.bigmodel.cn)
  - Get API key from dashboard

### Environment Setup
```bash
# Clone repository (if not already cloned)
git clone <repo-url>
cd hackathon-2-todo-phase-3

# Checkout feature branch
git checkout 007-ai-chatbot
```

---

## Backend Setup

### 1. Install Dependencies

```bash
cd backend

# Create virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install packages
uv pip install -r requirements.txt
```

**New dependencies for chatbot**:
```txt
# Add to requirements.txt
openai-agents[litellm]==<version>
litellm==<version>
fastmcp==<version>
dateparser==<version>
```

### 2. Configure Environment Variables

Create `.env` file in `backend/`:
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/todo_db

# Zhipu AI (GLM-4.5-air)
ZAI_API_KEY=your_zhipu_api_key_here

# Better Auth
JWT_SECRET=your_jwt_secret

# Logging
LOG_LEVEL=INFO
```

### 3. Start PostgreSQL

**Option A: Docker Compose** (Recommended)
```bash
# From backend/ directory
docker-compose up -d db
```

**docker-compose.yml**:
```yaml
version: '3.9'
services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: todo_db
      POSTGRES_USER: todo_user
      POSTGRES_PASSWORD: todo_pass
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

**Option B: Local PostgreSQL**
```bash
# Start PostgreSQL service
sudo systemctl start postgresql  # Linux
brew services start postgresql   # macOS
```

### 4. Run Database Migrations

```bash
# From backend/ directory
alembic upgrade head
```

This will:
- Create `conversations` table
- Create `messages` table
- Add `due_date` and `priority` columns to `tasks` table
- Create all necessary indexes

### 5. Start Backend Server

```bash
# From backend/ directory
uvicorn src.main:app --reload --port 8000
```

**Verify backend is running**:
```bash
curl http://localhost:8000/health
# Expected: {"status": "healthy", "database": "connected"}
```

**Access API Documentation**:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## Frontend Setup

### 1. Install Dependencies

```bash
cd frontend

# Install packages
npm install

# Install new chatbot dependencies
npm install @openai/chatkit-react
```

### 2. Configure Environment Variables

Create `.env.local` file in `frontend/`:
```bash
# API Backend
NEXT_PUBLIC_API_URL=http://localhost:8000

# Auth (if needed)
NEXT_PUBLIC_AUTH_URL=http://localhost:8000/auth
```

### 3. Start Development Server

```bash
# From frontend/ directory
npm run dev
```

**Access frontend**:
- http://localhost:3000

---

## Testing the Chatbot

### 1. Create a Test User

**Option A: Via API** (using curl)
```bash
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "Test123!@#"}'
```

**Option B: Via Frontend**
- Navigate to http://localhost:3000/signup
- Fill in email and password
- Click "Sign Up"

### 2. Login and Get Token

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "Test123!@#"}'

# Save the returned token
export AUTH_TOKEN="your_jwt_token_here"
```

### 3. Test Chat Endpoint (Backend)

**Send first message** (creates new conversation):
```bash
curl -N http://localhost:8000/api/v1/chat \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Add a task to buy groceries tomorrow",
    "conversation_id": null
  }'
```

**Expected SSE stream**:
```
data: {"type": "token", "content": "I've"}

data: {"type": "token", "content": " added"}

data: {"type": "token", "content": " a"}

data: {"type": "token", "content": " task"}

data: {"type": "done"}
```

**Continue conversation**:
```bash
# Use conversation_id from first response
curl -N http://localhost:8000/api/v1/chat \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What tasks are pending?",
    "conversation_id": "123e4567-e89b-12d3-a456-426614174000"
  }'
```

### 4. Test Conversation History

```bash
# List conversations
curl http://localhost:8000/api/v1/conversations \
  -H "Authorization: Bearer $AUTH_TOKEN"

# Get specific conversation
curl http://localhost:8000/api/v1/conversations/123e4567-e89b-12d3-a456-426614174000 \
  -H "Authorization: Bearer $AUTH_TOKEN"

# Get conversation messages
curl "http://localhost:8000/api/v1/conversations/123e4567-e89b-12d3-a456-426614174000/messages?page=1&limit=50" \
  -H "Authorization: Bearer $AUTH_TOKEN"
```

### 5. Test ChatKit Frontend

**Navigate to Chat Page**:
- http://localhost:3000/chat

**Test Scenarios**:

1. **Create Task**:
   - Type: "Add a task to buy groceries tomorrow"
   - Expected: Task created, confirmation message

2. **Set Priority**:
   - Type: "Create a high priority task to finish presentation"
   - Expected: Task created with priority=high

3. **Set Due Date**:
   - Type: "Remind me to call mom on Friday at 3pm"
   - Expected: Task with due_date parsed correctly

4. **List Tasks**:
   - Type: "What are my pending tasks?"
   - Expected: List of all pending tasks

5. **Complete Task**:
   - Type: "Mark task 1 as complete"
   - Expected: Task marked as completed

6. **Filter by Tag**:
   - Type: "Show me all tasks tagged with work"
   - Expected: Filtered list

7. **Use Template** (if templates exist):
   - Type: "Create a task from the weekly report template"
   - Expected: Task created from template

---

## Troubleshooting

### Backend Issues

**Issue**: `ModuleNotFoundError: No module named 'agents'`
```bash
# Solution: Install missing dependencies
pip install "openai-agents[litellm]"
pip install litellm fastmcp dateparser
```

**Issue**: `sqlalchemy.exc.OperationalError: could not connect to server`
```bash
# Solution: Check PostgreSQL is running
docker-compose ps  # or
sudo systemctl status postgresql

# Restart if needed
docker-compose restart db
```

**Issue**: `litellm.exceptions.AuthenticationError: Invalid API key`
```bash
# Solution: Check ZAI_API_KEY in .env
cat backend/.env | grep ZAI_API_KEY

# Get new key from https://open.bigmodel.cn
```

**Issue**: Migration fails with "relation already exists"
```bash
# Solution: Reset database (DEVELOPMENT ONLY!)
cd backend
alembic downgrade base
alembic upgrade head
```

### Frontend Issues

**Issue**: `Module not found: Can't resolve '@openai/chatkit-react'`
```bash
# Solution: Install missing package
cd frontend
npm install @openai/chatkit-react
```

**Issue**: CORS error in browser console
```bash
# Solution: Check CORS configuration in backend/src/main.py
# Ensure frontend URL is in allow_origins:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Issue**: "Network error" or "Failed to fetch"
```bash
# Solution: Check backend is running and NEXT_PUBLIC_API_URL is correct
# In frontend/.env.local:
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Chat/Streaming Issues

**Issue**: No streaming, response appears all at once
```bash
# Solution: Check SSE headers in backend
# Ensure response includes:
headers={
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "X-Accel-Buffering": "no"
}
```

**Issue**: "AI service temporarily unavailable"
```bash
# Solution: Check GLM-4.5-air API status
# Test API key:
curl -X POST "https://open.bigmodel.cn/api/paas/v4/chat/completions" \
  -H "Authorization: Bearer $ZAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "glm-4-air", "messages": [{"role": "user", "content": "test"}]}'
```

**Issue**: Date parsing not working ("tomorrow", "next Friday")
```bash
# Solution: Check dateparser is installed
pip show dateparser

# Test date parser in Python:
python -c "import dateparser; print(dateparser.parse('tomorrow'))"
```

---

## Development Workflow

### Running Tests

**Backend Tests**:
```bash
cd backend
pytest --cov=src tests/
```

**Frontend Tests**:
```bash
cd frontend
npm test
npm run test:e2e  # Playwright E2E tests
```

### Code Quality Checks

**Backend**:
```bash
cd backend
ruff check .        # Lint
black --check .     # Format check
mypy .              # Type check
```

**Frontend**:
```bash
cd frontend
npm run lint        # ESLint
npm run type-check  # TypeScript
```

### Database Management

**Create new migration**:
```bash
cd backend
alembic revision --autogenerate -m "Add new feature"
```

**View migration history**:
```bash
alembic history
```

**Rollback migration**:
```bash
alembic downgrade -1  # Go back one revision
```

---

## Key Endpoints Summary

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/chat` | POST | Send chat message (SSE streaming) |
| `/api/v1/conversations` | GET | List user's conversations |
| `/api/v1/conversations/{id}` | GET | Get conversation details |
| `/api/v1/conversations/{id}/messages` | GET | Get conversation messages |
| `/health` | GET | Health check |
| `/docs` | GET | Swagger UI |
| `/redoc` | GET | ReDoc documentation |

---

## Next Steps

After successfully running the quickstart:

1. **Implement TDD Workflow**:
   - Write tests FIRST (RED)
   - Implement feature (GREEN)
   - Refactor (REFACTOR)

2. **Add MCP Tools**:
   - Implement all task management tools in `backend/src/mcp/tools/`
   - Register tools with FastMCP server
   - Test tool invocations

3. **Build Chat Service**:
   - Implement `ChatService` in `backend/src/services/chat_service.py`
   - Integrate OpenAI Agents SDK with LiteLLM
   - Add conversation context loading

4. **Complete Frontend**:
   - Integrate @openai/chatkit-react
   - Add conversation sidebar
   - Implement message pagination

5. **Add Observability**:
   - Configure structured logging
   - Add metrics endpoints
   - Set up distributed tracing

---

## Useful Commands Cheat Sheet

```bash
# Backend
cd backend && uvicorn src.main:app --reload        # Start server
cd backend && alembic upgrade head                 # Run migrations
cd backend && pytest --cov=src tests/              # Run tests
cd backend && ruff check . && black . && mypy .    # Quality checks

# Frontend
cd frontend && npm run dev                         # Start dev server
cd frontend && npm test                            # Run unit tests
cd frontend && npm run test:e2e                    # Run E2E tests
cd frontend && npm run lint && npm run type-check  # Quality checks

# Database
docker-compose up -d db                            # Start PostgreSQL
docker-compose logs -f db                          # View logs
psql -U todo_user -d todo_db -h localhost          # Connect to DB

# Git
git status                                         # Check status
git add .                                          # Stage changes
git commit -m "feat: implement chatbot"            # Commit
git push origin 007-ai-chatbot                     # Push to remote
```

---

**Quickstart Complete**: You should now have a fully functional local development environment for the AI chatbot feature.

For implementation details, see:
- `plan.md` - Full implementation plan
- `data-model.md` - Database schema
- `contracts/chat-api.yaml` - API specification
- `research.md` - Technology research and decisions
