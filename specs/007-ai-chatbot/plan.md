# Implementation Plan: AI-Powered Task Management Chatbot

**Branch**: `007-ai-chatbot` | **Date**: 2025-12-23 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/007-ai-chatbot/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implement an AI-powered chatbot that enables natural language task management through conversational interface. Users can create, view, update, complete, and delete tasks by simply talking to the chatbot without navigating forms or clicking buttons. The chatbot will:

- Accept natural language input and interpret user intent (create tasks, set priorities, assign tags, set due dates)
- Maintain conversation history with context across multiple exchanges
- Stream responses in real-time for better UX
- Expose task operations as MCP tools that the AI agent can invoke
- Parse natural language date expressions ("tomorrow", "next Friday", "in 2 weeks")
- Handle ambiguous requests by asking clarifying questions
- Provide user-friendly error messages and graceful degradation

**Technical Approach**: Backend FastAPI application with OpenAI Agents SDK for orchestration, official MCP SDK for tool exposure, PostgreSQL for conversation/message persistence, and React/Next.js frontend with streaming chat interface. The system maintains stateless API architecture with database-persisted conversation state, loading last 50 messages as context window while retaining full history.

## Technical Context

**Language/Version**: Python 3.13+ (backend), TypeScript 5.7+ (frontend)
**Primary Dependencies**:
- Backend: FastAPI 0.100+, OpenAI Agents SDK, MCP SDK (official), SQLModel/SQLAlchemy 2.0+, dateparser (natural language date parsing), Pydantic v2
- Frontend: Next.js 15 (App Router), React 19, TanStack Query v5, Shadcn/ui, Tailwind CSS 4+, Zod, React Hook Form
**Storage**: PostgreSQL 16+ (Neon) for tasks, users, conversations, messages, templates, tags
**Testing**:
- Backend: pytest with pytest-cov (80%+ coverage target)
- Frontend: Vitest + React Testing Library (70%+ coverage target)
- E2E: Playwright for critical chat flows
**Target Platform**: Web application (Linux server backend, browser-based frontend)
**Project Type**: Web (full-stack) - separate backend/ and frontend/ directories
**Performance Goals**:
- Chat endpoint response time <3 seconds for 95% of requests
- Support 100+ concurrent chat sessions
- Streaming latency <100ms from OpenAI token to user display
- Natural language date parsing 95% accuracy
**Constraints**:
- OpenAI API rate limits (handled with retry logic and user feedback)
- Context window: Load last 50 messages (balance performance vs context)
- Stateless backend (conversation state in DB, not memory)
- HTTPS required, CORS configured, CSRF protection
**Scale/Scope**:
- Initial: 100+ concurrent users
- Conversations: Indefinite retention with pagination
- Messages: Up to thousands per conversation (50-message context window)
- Templates: User-specific (no cross-user sharing in MVP)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ Architecture & Design (Principle I)
- **Status**: COMPLIANT
- **Evidence**: Clear separation of layers: Frontend (React/Next.js) ↔ API (FastAPI) ↔ Services (MCP tools, business logic) ↔ Database (PostgreSQL). No direct database access from frontend. API routes will be thin (validation → service → response).
- **Implementation**: Backend services handle task operations, MCP server exposes tools, API layer validates and delegates, frontend consumes via OpenAPI-generated types.

### ✅ Code Quality (Principle II)
- **Status**: COMPLIANT
- **Evidence**: TypeScript strict mode (frontend), mypy strict mode (backend), explicit type hints everywhere, self-documenting code with clear intent.
- **Tooling**: ruff, black, mypy (backend); ESLint, Prettier, TypeScript (frontend).

### ✅ Testing - TDD (Principle III)
- **Status**: COMPLIANT
- **Evidence**: RED-GREEN-REFACTOR cycle mandatory. Backend 80%+ coverage (pytest), frontend 70%+ coverage (Vitest), E2E tests with Playwright for critical chat flows.
- **Test Strategy**: Unit tests for services/components, integration tests for API + database, E2E for full chat workflows.

### ✅ Data Management (Principle IV)
- **Status**: COMPLIANT
- **Evidence**: PostgreSQL as single source of truth. Atomic transactions for message persistence. Validation at all boundaries (frontend Zod, backend Pydantic). Alembic migrations for schema versioning.
- **Schema**: UUIDs for primary keys, foreign keys for referential integrity, indexes for performance, 3NF normalization.

### ✅ Error Handling (Principle V)
- **Status**: COMPLIANT
- **Evidence**: Graceful error handling with user-friendly messages. Frontend shows toast notifications for errors. Backend returns structured error responses with error codes. OpenAI API failures return "AI service temporarily unavailable" + preserve user message for retry.
- **Error Schema**: JSON with error code, message, details, timestamp, request_id.

### ✅ User Experience (Principle VI)
- **Status**: COMPLIANT
- **Evidence**: Shadcn/ui + Tailwind CSS for consistent design system. Streaming responses for real-time feedback. Loading states, empty states, error states. Toast notifications for success/error. Accessible (ARIA labels, keyboard navigation).
- **Feedback**: Every action shows immediate confirmation, optimistic UI where appropriate.

### ✅ Performance & Scalability (Principle VII)
- **Status**: COMPLIANT
- **Evidence**: Frontend code splitting (Next.js dynamic imports), image optimization, CDN for static assets. Backend async I/O, database indexing, connection pooling. Redis caching for sessions/task lists. Stateless architecture supports horizontal scaling.
- **Metrics**: <3s response time, <200KB initial bundle, 100+ concurrent users.

### ✅ Security & Safety (Principle VIII)
- **Status**: COMPLIANT
- **Evidence**: Input validation (frontend + backend), Better Auth integration (session/JWT), RBAC for authorization, HTTPS enforcement, CORS whitelist, CSRF protection, rate limiting (5 login attempts/min, 100 API requests/min/user), HTTP-only cookies.
- **OWASP**: Prevents SQL injection (ORM parameterization), XSS (CSP, escaped content), CSRF (tokens), broken auth (password hashing).

### ✅ Python Standards (Principle IX)
- **Status**: COMPLIANT
- **Evidence**: Python 3.13+, PEP 8 compliance (ruff), type checking (mypy strict), formatting (black), dependency management (uv), modern async patterns (FastAPI async endpoints).

### ✅ Development Workflow (Principle X)
- **Status**: COMPLIANT
- **Evidence**: Spec-driven (this plan follows spec.md), atomic commits, Conventional Commits format, feature branch (007-ai-chatbot), PHR and ADR documentation for significant decisions.

### ✅ Frontend Architecture (Principle XI)
- **Status**: COMPLIANT
- **Evidence**: Next.js 15 App Router + React 19, Tailwind CSS 4+ + Shadcn/ui, TanStack Query for server state, Zustand for client state, React Hook Form + Zod for forms, TypeScript 5.7+ strict mode.
- **Patterns**: Server Components by default, Client Components for interactivity, feature-specific components organized.

### ✅ API Design & Backend (Principle XII)
- **Status**: COMPLIANT
- **Evidence**: RESTful API design (/api/v1/chat, /api/v1/conversations), FastAPI with OpenAPI auto-generation, Pydantic schemas for validation, thin routes with service layer, proper HTTP status codes, pagination for conversation history.
- **Versioning**: /api/v1/ for API versioning.

### ✅ Authentication & Authorization (Principle XIII)
- **Status**: COMPLIANT
- **Evidence**: Better Auth integration (session-based with HTTP-only cookies), user isolation (user_id filtering), conversation ownership checks, rate limiting on auth endpoints.
- **Security**: Passwords hashed (bcrypt/Argon2 via Better Auth), CSRF protection, session expiration.

### ✅ Database Architecture (Principle XIV)
- **Status**: COMPLIANT
- **Evidence**: PostgreSQL 16+ with 3NF schema design, UUIDs for primary keys, foreign keys for referential integrity, indexes for performance (user_id, conversation_id), Alembic migrations with reversibility.
- **Schema**: conversations, messages, tasks (extended), tags, templates tables.

### ✅ Web Security (Principle XV)
- **Status**: COMPLIANT
- **Evidence**: Input validation (Pydantic + Zod), XSS prevention (CSP headers, escaped content), CSRF tokens, CORS whitelist (no * in production), rate limiting, HTTPS enforcement, Dependabot for dependency scanning.
- **OWASP Top 10**: All major vulnerabilities addressed.

### ✅ Accessibility & Responsive (Principle XVI)
- **Status**: COMPLIANT
- **Evidence**: WCAG 2.1 AA compliance (semantic HTML, ARIA labels, keyboard navigation, 4.5:1 contrast). Responsive design (mobile-first, Tailwind breakpoints), 44x44px touch targets.
- **Testing**: Keyboard navigation, screen reader support, mobile/tablet/desktop testing.

### ✅ Deployment & Infrastructure (Principle XVII)
- **Status**: COMPLIANT
- **Evidence**: Docker + Docker Compose for local dev, CI/CD via GitHub Actions, environment variables for secrets, deployment targets (Vercel frontend, Railway/Render backend + PostgreSQL).
- **Containers**: Multi-stage Docker builds, postgres:16-alpine, FastAPI + Next.js containers.

### ✅ Monitoring & Observability (Principle XVIII)
- **Status**: COMPLIANT
- **Evidence**: Structured JSON logging (request_id, user_id, timestamp, tool invocations), metrics for response time/error rates/tool usage, distributed tracing for OpenAI + MCP calls, health check endpoint (/health), Sentry for error tracking.
- **Logs**: All tool invocations logged with parameters and results.

### ✅ Performance Optimization (Principle XIX)
- **Status**: COMPLIANT
- **Evidence**: Frontend: Next.js dynamic imports, <200KB bundle, Image optimization, CDN (Vercel Edge). Backend: Database indexes, connection pooling, async endpoints, Redis caching.
- **Optimizations**: Prefetching, lazy loading, query optimization (avoid N+1).

### ✅ Type Safety & API Contracts (Principle XX)
- **Status**: COMPLIANT
- **Evidence**: End-to-end type safety via OpenAPI. Backend Pydantic schemas → FastAPI auto-generates /openapi.json → Frontend TypeScript types generated via openapi-typescript. Compile-time type checking, IDE autocomplete.
- **Workflow**: Pydantic models define contracts, types sync automatically.

### Summary
**Total Gates**: 20 principles evaluated
**Passed**: 20 ✅
**Failed**: 0 ❌
**Violations Requiring Justification**: None

**Verdict**: ✅ **PASS** - All constitution principles satisfied. Proceed to Phase 0 research.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   ├── conversation.py        # Conversation SQLModel
│   │   ├── message.py             # Message SQLModel
│   │   ├── task.py                # Extended Task model (add due_date, priority)
│   │   ├── tag.py                 # Tag model
│   │   └── template.py            # Template model
│   ├── services/
│   │   ├── chat_service.py        # OpenAI Agent orchestration
│   │   ├── conversation_service.py # Conversation CRUD
│   │   ├── message_service.py     # Message persistence
│   │   ├── task_service.py        # Existing task service (extend)
│   │   ├── template_service.py    # Template operations
│   │   └── date_parser_service.py # Natural language date parsing
│   ├── mcp/
│   │   ├── server.py              # MCP server setup
│   │   └── tools/
│   │       ├── task_tools.py      # add_task, list_tasks, update_task, etc.
│   │       ├── tag_tools.py       # add_tag, remove_tag, filter_by_tag
│   │       └── template_tools.py  # list_templates, create_from_template
│   ├── api/
│   │   └── v1/
│   │       ├── chat.py            # POST /api/v1/chat (streaming)
│   │       ├── conversations.py   # GET /api/v1/conversations
│   │       └── health.py          # GET /health
│   ├── schemas/
│   │   ├── chat.py                # ChatRequest, ChatResponse Pydantic schemas
│   │   ├── conversation.py        # ConversationResponse schemas
│   │   └── message.py             # MessageResponse schemas
│   ├── core/
│   │   ├── config.py              # Settings (OpenAI API key, DB URL)
│   │   ├── database.py            # SQLModel engine, session
│   │   ├── auth.py                # Better Auth integration
│   │   └── logging.py             # Structured logging setup
│   └── main.py                    # FastAPI app entrypoint
├── tests/
│   ├── unit/
│   │   ├── test_services/
│   │   ├── test_mcp_tools/
│   │   └── test_date_parser.py
│   ├── integration/
│   │   ├── test_api_chat.py       # Test chat endpoint
│   │   └── test_conversation_persistence.py
│   └── conftest.py                # Pytest fixtures
├── alembic/
│   └── versions/
│       └── xxx_add_conversation_message_tables.py
├── requirements.txt
├── Dockerfile
└── docker-compose.yml

frontend/
├── src/
│   ├── app/
│   │   ├── (auth)/
│   │   │   ├── login/page.tsx
│   │   │   └── signup/page.tsx
│   │   ├── chat/
│   │   │   └── page.tsx           # Main chat interface
│   │   ├── layout.tsx
│   │   └── page.tsx               # Landing/dashboard
│   ├── components/
│   │   ├── ui/                    # Shadcn components (button, input, etc.)
│   │   ├── features/
│   │   │   └── chat/
│   │   │       ├── ChatInterface.tsx  # Main chat component
│   │   │       ├── MessageList.tsx    # Display messages
│   │   │       ├── MessageInput.tsx   # User input
│   │   │       ├── StreamingMessage.tsx # Streaming text display
│   │   │       └── ConversationList.tsx # Sidebar with conversations
│   │   └── layout/
│   │       ├── Header.tsx
│   │       └── Sidebar.tsx
│   ├── lib/
│   │   ├── api-client.ts          # Fetch wrapper for API calls
│   │   ├── stream-handler.ts     # SSE stream processing
│   │   └── utils.ts               # Utility functions
│   ├── hooks/
│   │   ├── useChat.ts             # Chat logic with TanStack Query
│   │   ├── useConversations.ts   # Conversation history
│   │   └── useStreamingMessage.ts # Streaming message state
│   ├── types/
│   │   └── api.ts                 # Generated from OpenAPI spec
│   └── store/
│       └── chat-store.ts          # Zustand store for UI state
├── tests/
│   ├── unit/
│   │   └── components/
│   └── e2e/
│       └── chat-workflow.spec.ts  # Playwright E2E test
├── package.json
├── tsconfig.json
├── tailwind.config.ts
├── next.config.js
└── Dockerfile
```

**Structure Decision**: Selected **Option 2: Web Application** structure with separate `backend/` and `frontend/` directories. This matches the constitution's full-stack web architecture pattern. Backend uses FastAPI with MCP server integration, frontend uses Next.js 15 App Router. Both are independently deployable and follow the project's existing structure (matching 005-task-management and 006-landing-page-ui patterns).

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**No violations** - All constitution principles satisfied.

---

## Implementation Priorities

### Phase 0: Foundation (Complete)
✅ Research completed for all technologies
✅ Architecture decisions documented
✅ OpenAI Agents SDK + LiteLLM integration confirmed
✅ FastMCP for MCP server confirmed
✅ ChatKit React for frontend confirmed
✅ Database schema designed

### Phase 1: Backend Core (Priority: P0)
**Duration**: Week 1-2
**Dependencies**: None

1. **Database Setup**
   - Run Alembic migration (conversations, messages, task extensions)
   - Verify indexes created
   - Test data seeding for development

2. **Agent Service**
   - Implement `ChatService` with OpenAI Agents SDK
   - Configure LiteLLM with GLM-4.5-air model
   - Add conversation context loading (last 50 messages)
   - Implement streaming support

3. **MCP Tools**
   - Implement task management tools (add, list, update, complete, delete)
   - Implement tag tools (add_tag, remove_tag, list_tags, filter_by_tag)
   - Implement template tools (list_templates, create_from_template)
   - Register all tools with FastMCP server

4. **Date Parser Service**
   - Implement natural language date parsing with dateparser
   - Add validation and error handling
   - Test common expressions (tomorrow, next week, etc.)

5. **API Endpoints**
   - `/api/v1/chat` - Streaming chat endpoint (SSE)
   - `/api/v1/conversations` - List conversations
   - `/api/v1/conversations/{id}/messages` - Get messages
   - `/health` - Health check endpoint

**Exit Criteria**:
- All backend tests passing (80%+ coverage)
- Chat endpoint streaming works
- MCP tools invokable via agent
- Date parsing accurate for common expressions

### Phase 2: Frontend Core (Priority: P0)
**Duration**: Week 2-3
**Dependencies**: Phase 1 complete

1. **ChatKit Integration**
   - Install @openai/chatkit-react
   - Create `/chat` page with ChatKit component
   - Configure SSE connection to backend
   - Test streaming message display

2. **Conversation Management**
   - Conversation list sidebar
   - Create new conversation button
   - Switch between conversations
   - Display conversation titles

3. **Message Display**
   - Render user/assistant messages
   - Show streaming indicators
   - Display timestamps
   - Scroll to bottom on new message

4. **Authentication Integration**
   - Connect to Better Auth
   - Add auth headers to API calls
   - Handle token refresh
   - Protected routes

**Exit Criteria**:
- Chat interface functional
- Messages stream in real-time
- Users can create and switch conversations
- Frontend tests passing (70%+ coverage)

### Phase 3: Polish & Testing (Priority: P1)
**Duration**: Week 3-4
**Dependencies**: Phase 1 & 2 complete

1. **E2E Testing**
   - Playwright tests for critical flows
   - Test task creation via chat
   - Test conversation history
   - Test error handling

2. **Error Handling**
   - Graceful OpenAI API failures
   - User-friendly error messages
   - Retry logic with exponential backoff
   - Preserve failed messages for retry

3. **Observability**
   - Structured JSON logging
   - Metrics endpoints (response time, error rates)
   - Distributed tracing spans
   - Sentry error tracking integration

4. **UX Improvements**
   - Loading states
   - Empty states
   - Error states
   - Keyboard shortcuts

**Exit Criteria**:
- All E2E tests passing
- Error scenarios handled gracefully
- Observability in place
- UX polished

### Phase 4: Deployment (Priority: P1)
**Duration**: Week 4-5
**Dependencies**: Phase 3 complete

1. **Docker Setup**
   - Dockerfile for backend
   - Dockerfile for frontend
   - docker-compose.yml for local dev
   - Multi-stage builds

2. **CI/CD Pipeline**
   - GitHub Actions workflow
   - Lint, format, type-check, test
   - Build and deploy to staging
   - Manual production deploy

3. **Environment Configuration**
   - Production environment variables
   - Secret management
   - Database connection pooling
   - Rate limiting

4. **Monitoring**
   - Health check endpoints
   - Uptime monitoring
   - Log aggregation
   - Alert configuration

**Exit Criteria**:
- Docker containers working
- CI/CD pipeline passing
- Deployed to staging successfully
- Monitoring configured

---

## Next Steps

After completing `/sp.plan`:

1. **Run** `/sp.tasks` - Generate task breakdown from this plan
2. **Implement** TDD workflow:
   - RED: Write failing tests
   - GREEN: Implement feature
   - REFACTOR: Clean up code
3. **Commit** regularly with conventional commits format
4. **Document** architecturally significant decisions in ADRs
5. **Review** with team before major milestones

---

**Implementation Plan Complete**: Ready for task generation via `/sp.tasks`.
