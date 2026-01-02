# TodoMore - AI-Powered Task Management Platform

> A modern, full-stack task management application with AI integration, featuring a Next.js frontend, FastAPI backend, and MCP server for intelligent task assistance.

## Overview

TodoMore is a comprehensive task management platform that combines powerful features with an intuitive interface. Built with modern technologies and AI capabilities, it helps users organize, track, and complete tasks efficiently across multiple views and devices.

### Key Features

- **AI-Powered Chatbot** - Intelligent task assistance via Model Context Protocol (MCP)
- **Multiple Views** - List, Grid, Kanban, Calendar, and Dashboard analytics
- **Advanced Task Management** - Tags, subtasks, priorities, due dates with timezone support
- **Recurring Tasks** - Automated task creation with flexible recurrence rules
- **Task Templates** - Quick task creation from predefined templates
- **Drag & Drop** - Intuitive task organization with @dnd-kit
- **Keyboard Shortcuts** - Quick access with Cmd/Ctrl+K command palette
- **Mobile-Friendly** - Swipe gestures and responsive design
- **Theme Picker** - Customizable themes with smooth animations
- **Onboarding Tour** - Guided walkthrough for new users
- **Real-time Updates** - Optimistic UI updates with TanStack Query

## Technology Stack

### Frontend

| Technology | Version | Purpose |
|------------|---------|---------|
| [Next.js](https://nextjs.org/) | 15+ | React framework with App Router |
| [React](https://react.dev/) | 19+ | UI library |
| [TypeScript](https://www.typescriptlang.org/) | 5.7+ | Type safety |
| [TanStack Query](https://tanstack.com/query/latest) | v5 | Data fetching and caching |
| [Shadcn/ui](https://ui.shadcn.com/) | Latest | Component library (Radix UI) |
| [Tailwind CSS](https://tailwindcss.com/) | 3.4+ | Utility-first styling |
| [Framer Motion](https://www.framer.com/motion/) | 12+ | Animations |
| [Recharts](https://recharts.org/) | 3+ | Data visualization |
| [@dnd-kit](https://dndkit.com/) | Latest | Drag-and-drop |
| [cmdk](https://cmdk.paco.me/) | Latest | Command palette |
| [date-fns](https://date-fns.org/) | 4+ | Date utilities |
| [Zustand](https://zustand-demo.pmnd.rs/) | 5+ | Client state |
| [Vitest](https://vitest.dev/) | 4+ | Testing framework |

### Backend

| Technology | Version | Purpose |
|------------|---------|---------|
| [Python](https://www.python.org/) | 3.13+ | Programming language |
| [FastAPI](https://fastapi.tiangolo.com/) | 0.100+ | Web framework |
| [SQLModel](https://sqlmodel.tiangolo.com/) | Latest | ORM (SQLAlchemy + Pydantic) |
| [Alembic](https://alembic.sqlalchemy.org/) | 1.13+ | Database migrations |
| [PostgreSQL](https://www.postgresql.org/) | 16+ | Database (Neon serverless) |
| [Pydantic](https://docs.pydantic.dev/) | 2+ | Data validation |
| [asyncpg](https://magicstack.github.io/asyncpg/) | 0.29+ | Async PostgreSQL driver |
| [Pytest](https://docs.pytest.org/) | 7+ | Testing framework |

### MCP Server (AI Integration)

| Technology | Version | Purpose |
|------------|---------|---------|
| [FastMCP](https://github.com/jlowin/fastmcp) | 2.0+ | Model Context Protocol server |
| [FastAPI](https://fastapi.tiangolo.com/) | 0.100+ | HTTP framework |
| [asyncpg](https://magicstack.github.io/asyncpg/) | 0.29+ | Direct database access |
| [python-dateutil](https://dateutil.readthedocs.io/) | 2.8+ | Date parsing |

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                          User/AI                             │
└─────────────────┬──────────────────────┬────────────────────┘
                  │                       │
                  ▼                       ▼
         ┌─────────────────┐    ┌──────────────────┐
         │  Next.js Frontend│    │   MCP Server     │
         │   (Port 3000)    │    │  (AI Assistant)  │
         └────────┬─────────┘    └────────┬─────────┘
                  │                       │
                  ▼                       │
         ┌─────────────────┐             │
         │  FastAPI Backend │◄────────────┘
         │   (Port 8000)    │
         └────────┬─────────┘
                  │
                  ▼
         ┌─────────────────┐
         │   PostgreSQL     │
         │ (Neon Serverless)│
         └──────────────────┘
```

### Component Architecture

```
frontend/
├── app/                    # Next.js App Router pages
├── components/             # React components
│   ├── calendar/          # Calendar view
│   ├── dashboard/         # Analytics dashboard
│   ├── kanban/            # Kanban board
│   ├── landing/           # Landing page sections
│   ├── mobile/            # Mobile-specific components
│   ├── onboarding/        # Tour components
│   ├── sidebar/           # Navigation
│   ├── tasks/             # Task management
│   └── ui/                # Reusable UI (Shadcn)
├── hooks/                 # Custom React hooks
└── lib/                   # Utilities and API client

backend/
├── src/
│   ├── api/               # API endpoints
│   ├── core/              # Core utilities (auth, config)
│   ├── models/            # Database models
│   ├── schemas/           # Pydantic schemas
│   ├── services/          # Business logic
│   └── db/                # Database utilities
└── alembic/               # Database migrations

mcp_server/
└── main.py                # MCP tools for AI integration
```

## Prerequisites

Before you begin, ensure you have the following installed:

- **Node.js** 18+ and **npm** (for frontend)
- **Python** 3.13+ (for backend and MCP server)
- **PostgreSQL** 16+ or access to [Neon](https://neon.tech/) (serverless PostgreSQL)
- **Git** for version control

Optional but recommended:
- **Docker** and **Docker Compose** (for containerized deployment)
- **uv** (fast Python package manager) - Install with: `pip install uv`

## Quick Start

### Option 1: Docker Compose (Recommended)

The fastest way to run the entire stack:

```bash
# 1. Clone the repository
git clone <repository-url>
cd hackathon-2-todo-phase-3

# 2. Set up environment variables
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local

# 3. Configure your DATABASE_URL in backend/.env
# Example: DATABASE_URL=postgresql+asyncpg://user:password@host:5432/todoly

# 4. Start all services
docker-compose up --build
```

Access the application:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Option 2: Local Development

For development with hot-reload:

#### 1. Backend Setup

```bash
cd backend

# Create virtual environment (using uv - recommended)
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -e ".[test]"

# Set up environment variables
cp .env.example .env
# Edit .env and add your DATABASE_URL

# Run database migrations
alembic upgrade head

# Start development server
uvicorn src.main:app --reload
```

Backend will be available at http://localhost:8000

#### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env.local
# Edit .env.local and set NEXT_PUBLIC_API_URL=http://localhost:8000

# Start development server
npm run dev
```

Frontend will be available at http://localhost:3000

#### 3. MCP Server Setup (Optional)

The MCP server enables AI assistant integration:

```bash
cd mcp_server

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your DATABASE_URL

# Start MCP server
uvicorn main:app --reload --port 8001
```

MCP server will be available at http://localhost:8001

## Environment Variables

### Backend (.env)

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/todoly

# JWT Authentication
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
ALLOWED_ORIGINS=http://localhost:3000,https://your-domain.com

# Environment
ENVIRONMENT=development  # development, staging, production
```

### Frontend (.env.local)

```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# Optional: Analytics, monitoring, etc.
NEXT_PUBLIC_ENABLE_ANALYTICS=false
```

### MCP Server (.env)

```bash
# Database (same as backend)
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/todoly

# Optional: Frontend URL for CORS
FRONTEND_URL=http://localhost:3000
```

## Database Setup

### Using Neon (Recommended for Production)

1. Sign up at [Neon](https://neon.tech/)
2. Create a new project
3. Copy the connection string
4. Update `DATABASE_URL` in your `.env` files

### Using Local PostgreSQL

```bash
# Install PostgreSQL 16+
# Create database
createdb todoly

# Update DATABASE_URL
DATABASE_URL=postgresql+asyncpg://localhost:5432/todoly

# Run migrations
cd backend && alembic upgrade head
```

## Development Workflow

### Running Tests

**Backend:**
```bash
cd backend

# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=html

# Run specific test file
uv run pytest tests/test_tasks.py

# Run in watch mode
uv run pytest-watch
```

**Frontend:**
```bash
cd frontend

# Run unit tests
npm test

# Run with coverage
npm run test:cov

# Run in watch mode
npm run test:watch

# Run E2E tests (Playwright)
npm run test:e2e
```

### Code Quality Checks

**Backend:**
```bash
cd backend

# Lint with Ruff
uv run ruff check src tests

# Format with Black
uv run black src tests

# Type check with Mypy
uv run mypy src tests

# Run all checks
uv run poe check
```

**Frontend:**
```bash
cd frontend

# Lint with ESLint
npm run lint

# Format with Prettier
npm run format

# Check formatting
npm run format:check

# Type check with TypeScript
npm run type-check
```

### Database Migrations

**Create a new migration:**
```bash
cd backend

# Auto-generate migration from model changes
alembic revision --autogenerate -m "Add new field to tasks"

# Review the generated migration file in alembic/versions/
# Edit if necessary

# Apply migration
alembic upgrade head
```

**Common migration commands:**
```bash
# View current version
alembic current

# View migration history
alembic history

# Downgrade one version
alembic downgrade -1

# Upgrade to specific version
alembic upgrade <revision_id>

# Reset database (development only!)
alembic downgrade base
alembic upgrade head
```

## API Documentation

The FastAPI backend automatically generates interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### Key API Endpoints

#### Authentication

```bash
POST /api/auth/register     # Register new user
POST /api/auth/login        # Login and get JWT token
POST /api/auth/refresh      # Refresh access token
GET  /api/auth/me           # Get current user
```

#### Tasks

```bash
GET    /api/tasks           # List tasks (with filters)
POST   /api/tasks           # Create task
GET    /api/tasks/{id}      # Get task details
PATCH  /api/tasks/{id}      # Update task
DELETE /api/tasks/{id}      # Soft delete task
PATCH  /api/tasks/{id}/toggle  # Toggle task status
```

#### Tags

```bash
GET    /api/tags            # List user's tags
POST   /api/tags            # Create tag
GET    /api/tags/{id}       # Get tag details
PATCH  /api/tags/{id}       # Update tag
DELETE /api/tags/{id}       # Delete tag
```

#### Subtasks

```bash
GET    /api/subtasks        # List subtasks for task
POST   /api/subtasks        # Create subtask
PATCH  /api/subtasks/{id}   # Update subtask
DELETE /api/subtasks/{id}   # Delete subtask
```

#### Templates

```bash
GET    /api/templates       # List task templates
POST   /api/templates       # Create template
GET    /api/templates/{id}  # Get template
DELETE /api/templates/{id}  # Delete template
```

#### Analytics

```bash
GET /api/analytics/overview      # Task statistics
GET /api/analytics/productivity  # Productivity metrics
```

## MCP Tools (AI Integration)

The MCP server exposes these tools for AI assistants:

| Tool | Description |
|------|-------------|
| `add_task` | Create a new task with optional tags |
| `list_tasks` | List tasks with status/priority filters |
| `complete_task` | Mark a task as completed |
| `update_task` | Update task fields |
| `delete_task` | Soft delete a task |

**Example MCP Tool Usage:**

```json
{
  "tool": "add_task",
  "parameters": {
    "title": "Write documentation",
    "description": "Create comprehensive README",
    "priority": "high",
    "due_date": "2024-01-15",
    "tags": ["documentation", "urgent"]
  }
}
```

## Features in Detail

### 1. Multiple Task Views

- **List View**: Classic task list with sorting and filtering
- **Grid View**: Card-based layout for visual overview
- **Kanban Board**: Drag-and-drop task management by status
- **Calendar View**: Time-based task visualization
- **Dashboard**: Analytics and productivity insights

### 2. AI Chatbot Integration

Powered by the MCP server, the AI chatbot can:
- Create, update, and complete tasks via natural language
- Answer questions about your tasks
- Provide task recommendations
- Help organize and prioritize work

### 3. Smart Task Management

- **Tags**: Color-coded labels for organization
- **Subtasks**: Break down complex tasks
- **Priorities**: Low, Medium, High priority levels
- **Due Dates**: Timezone-aware date handling
- **Recurring Tasks**: Daily, weekly, monthly patterns
- **Templates**: Quick task creation from saved templates

### 4. Keyboard Shortcuts

Press `Cmd/Ctrl + K` to open the command palette:
- Quick task creation
- Navigate between views
- Search tasks
- Access recent items

### 5. Mobile Experience

- **Swipe Gestures**: Swipe to complete or delete tasks
- **Responsive Design**: Optimized for all screen sizes
- **Touch-Friendly**: Large tap targets and mobile-first UI

## Deployment

### Frontend (Vercel)

```bash
cd frontend

# Install Vercel CLI
npm i -g vercel

# Deploy
vercel

# Set environment variables in Vercel dashboard
# NEXT_PUBLIC_API_URL=https://your-backend-url.com
```

### Backend (Docker/Railway/Render)

**Docker:**
```bash
cd backend
docker build -t todoly-backend .
docker run -p 8000:8000 --env-file .env todoly-backend
```

**Railway/Render:**
1. Connect your Git repository
2. Set environment variables
3. Configure build command: `uv pip install -e .`
4. Configure start command: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`

### MCP Server (Vercel Serverless)

```bash
cd mcp_server

# Deploy to Vercel
vercel

# Set DATABASE_URL in Vercel dashboard
```

## Troubleshooting

### Backend Issues

**Migration Errors:**
```bash
# Reset database (development only)
cd backend
alembic downgrade base
alembic upgrade head

# Check current version
alembic current
```

**CORS Errors:**
Ensure `ALLOWED_ORIGINS` in backend `.env` includes your frontend URL.

**Database Connection:**
Verify `DATABASE_URL` format:
```
postgresql+asyncpg://user:password@host:port/database
```

### Frontend Issues

**Module Not Found:**
```bash
cd frontend
rm -rf node_modules package-lock.json .next
npm install
npm run dev
```

**Environment Variables Not Loading:**
Restart dev server after changing `.env.local`.

**Type Errors:**
```bash
npm run type-check
```

### MCP Server Issues

**Connection Refused:**
Verify the MCP server is running and the port is not in use.

**Database Access:**
Ensure the MCP server has the same `DATABASE_URL` as the backend.

## Contributing

We welcome contributions! Please follow these guidelines:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Follow code style**:
   - Backend: PEP 8, Black formatting, type hints
   - Frontend: TypeScript strict mode, Prettier formatting
4. **Write tests** for new features
5. **Run linters and tests**:
   ```bash
   # Backend
   cd backend && uv run poe check

   # Frontend
   cd frontend && npm run lint && npm test
   ```
6. **Commit with descriptive messages**
7. **Push to your fork**: `git push origin feature/amazing-feature`
8. **Open a Pull Request**

### Development Guidelines

See detailed guidelines in:
- [Backend Guidelines](/home/saifullah/projects/agentic-ai/hackathon-2-todo-phase-3/backend/CLAUDE.md)
- [Frontend Guidelines](/home/saifullah/projects/agentic-ai/hackathon-2-todo-phase-3/frontend/CLAUDE.md)
- [MCP Server Guidelines](/home/saifullah/projects/agentic-ai/hackathon-2-todo-phase-3/mcp_server/CLAUDE.md)
- [Project Guidelines](/home/saifullah/projects/agentic-ai/hackathon-2-todo-phase-3/CLAUDE.md)

## Project Structure

```
hackathon-2-todo-phase-3/
├── backend/                 # FastAPI backend
│   ├── alembic/            # Database migrations
│   ├── src/
│   │   ├── api/            # API routes
│   │   ├── core/           # Core utilities
│   │   ├── models/         # Database models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic
│   │   └── main.py         # FastAPI app
│   ├── tests/              # Backend tests
│   ├── pyproject.toml      # Python dependencies
│   └── README.md           # Backend documentation
│
├── frontend/               # Next.js frontend
│   ├── app/               # App Router pages
│   ├── components/        # React components
│   ├── hooks/             # Custom hooks
│   ├── lib/               # Utilities
│   ├── tests/             # Frontend tests
│   ├── package.json       # Node dependencies
│   └── README.md          # Frontend documentation
│
├── mcp_server/            # MCP AI integration server
│   ├── main.py           # FastMCP server
│   ├── requirements.txt  # Python dependencies
│   └── vercel.json       # Vercel config
│
├── docker-compose.yml    # Docker orchestration
├── CLAUDE.md            # Development guidelines
└── README.md            # This file
```

## Performance Considerations

### Frontend
- **Code Splitting**: Next.js automatic code splitting
- **Image Optimization**: Next.js Image component
- **Query Caching**: TanStack Query with smart cache invalidation
- **Lazy Loading**: Dynamic imports for heavy components
- **Memoization**: React.memo for expensive renders

### Backend
- **Connection Pooling**: SQLAlchemy async pool
- **Query Optimization**: Indexed queries, pagination
- **Caching**: Response caching for read-heavy endpoints
- **Async Operations**: FastAPI async routes

## Security

- **Authentication**: JWT tokens with refresh mechanism
- **Password Hashing**: Bcrypt with salt rounds
- **SQL Injection Protection**: SQLModel/SQLAlchemy ORM
- **XSS Prevention**: React automatic escaping
- **CORS**: Configured for specific origins
- **Environment Variables**: Sensitive data in .env files
- **Soft Deletes**: No permanent data loss

## License

This project is part of the Agentic AI Hackathon. Please refer to the hackathon terms and conditions.

## Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Frontend powered by [Next.js](https://nextjs.org/) and [React](https://react.dev/)
- UI components from [Shadcn/ui](https://ui.shadcn.com/)
- Database hosted on [Neon](https://neon.tech/)
- AI integration via [FastMCP](https://github.com/jlowin/fastmcp)

## Support

For questions or issues:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review component-specific READMEs
3. Search existing issues
4. Open a new issue with detailed information

## Changelog

### Phase 3 (Current)
- Added MCP server for AI assistant integration
- Implemented 5 core MCP tools (add, list, complete, update, delete tasks)
- Enhanced AI chatbot with conversation history
- Added Vercel deployment support for MCP server

### Phase 2
- Multiple task views (List, Grid, Kanban, Calendar, Dashboard)
- Added Framer Motion animations
- Implemented drag-and-drop with @dnd-kit
- Added command palette with cmdk
- Mobile swipe gestures
- Onboarding tour
- Theme picker
- Tags with color coding
- Subtasks with auto-completion
- Recurring tasks
- Task templates

### Phase 1
- Initial project setup
- FastAPI backend with PostgreSQL
- Next.js frontend with TypeScript
- Basic task CRUD operations
- User authentication
- RESTful API design
- Docker containerization

---

**Built with ❤️ for the Agentic AI Hackathon**
