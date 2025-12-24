# Port Configuration Changes

## Summary
Updated all backend API references from port **8000** to port **9000**.

## Services

### Backend (FastAPI)
- **Old**: `http://localhost:8000`
- **New**: `http://localhost:9000`
- **File**: `backend/src/main.py`

### MCP Server (FastMCP)
- **Port**: `http://localhost:8001/mcp` (unchanged)
- **File**: `backend/src/mcp_server/server.py`

### Frontend (Next.js)
- **Port**: `http://localhost:3000` (unchanged)

## Files Updated

### Configuration Files
1. ✅ `frontend/.env` - Updated `NEXT_PUBLIC_API_URL`
2. ✅ `docker-compose.yml` - Updated backend port mapping and environment variables
3. ✅ `backend/src/main.py` - Updated uvicorn port

### Frontend Components
4. ✅ `frontend/components/features/chat/chat-widget.tsx` - Updated fallback URL
5. ✅ `frontend/components/features/chat/ChatInterface.tsx` - Updated fallback URL
6. ✅ `frontend/components/kanban/KanbanBoard.tsx` - Updated fallback URL

### Tests
7. ✅ `frontend/tests/e2e/task-management.spec.ts` - Updated API_URL

## How to Run

### Development Mode

```bash
# Terminal 1: Start MCP Server
cd backend
uv run --with mcp python -m src.mcp_server.server
# → http://localhost:8001/mcp

# Terminal 2: Start FastAPI Backend
cd backend
python -m src.main
# → http://localhost:9000
# → API Docs: http://localhost:9000/docs

# Terminal 3: Start Frontend
cd frontend
npm run dev
# → http://localhost:3000
```

### Docker Compose

```bash
docker-compose up
# Frontend: http://localhost:3000
# Backend: http://localhost:9000
```

## Environment Variables

Make sure your `.env` files have:

**frontend/.env**
```env
NEXT_PUBLIC_API_URL=http://localhost:9000
```

**backend/.env**
```env
DATABASE_URL=postgresql+asyncpg://...
OPENROUTER_API_KEY=sk-or-v1-...
GEMINI_API_KEY=...
```

## API Endpoints

- FastAPI Backend: `http://localhost:9000/api/v1/*`
- ChatKit Endpoint: `http://localhost:9000/chatkit`
- Health Check: `http://localhost:9000/health`
- API Documentation: `http://localhost:9000/docs`
- MCP Server: `http://localhost:8001/mcp`

## Testing

```bash
# Test backend health
curl http://localhost:9000/health

# Test MCP server tools
curl http://localhost:8001/list_tools

# Test ChatKit (with auth token)
curl -X POST http://localhost:9000/chatkit \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'
```
