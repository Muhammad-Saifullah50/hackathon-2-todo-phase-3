<!--
Sync Impact Report:
- Version: 1.0.0 → 2.0.0
- Rationale: MAJOR version bump - transformation from CLI Todo to Full-Stack Web Application
- Parent: CLI Todo Application Constitution v1.0.0 (retained 8 of 10 core principles with web adaptations)
- Modified principles:
  * I. Architecture & Design: CLI layers → Web layers (Frontend ↔ API ↔ Services ↔ Database)
  * VI. User Experience: CLI UX → Web UI/UX (rich/questionary → React/Next.js/Shadcn/Tailwind)
  * VII. Data Management: JSON storage → PostgreSQL/MySQL with ORM (Prisma/SQLAlchemy)
- New principles added:
  * XI. Frontend Architecture - Professional UI Generation (React/Next.js/Tailwind/Shadcn)
  * XII. API Design & Backend Architecture (RESTful standards, FastAPI/Django)
  * XIII. Authentication & Authorization (JWT/Session-based, OAuth, RBAC)
  * XIV. Database Architecture & Migration (PostgreSQL, schema versioning, Prisma/SQLAlchemy)
  * XV. Web Security (OWASP Top 10, CORS, CSRF, CSP, rate limiting)
  * XVI. Accessibility & Responsive Design (WCAG 2.1 AA, mobile-first)
  * XVII. Deployment & Infrastructure (Docker, CI/CD, environment management)
  * XVIII. Monitoring & Observability (structured logging, Sentry, APM, health checks)
  * XIX. Performance Optimization (frontend bundle size, backend caching, CDN)
  * XX. Type Safety & API Contracts (OpenAPI, end-to-end type safety)
- Retained unchanged:
  * II. Code Quality
  * III. Testing (expanded to include E2E with Playwright)
  * V. Error Handling
  * VIII. Performance & Scalability (expanded for web scale)
  * IX. Python Standards (backend)
  * X. Development Workflow
- New sections added:
  * Full-Stack Tooling & Environment (frontend + backend tooling)
  * Web Application Quality Gates (expanded checklist)
  * Migration Roadmap (CLI → Full-Stack Web, 6-phase plan)
- Templates requiring updates:
  ✅ plan-template.md - Constitution Check section expanded for web principles
  ✅ spec-template.md - Requirements expanded to include frontend/backend/infrastructure
  ✅ tasks-template.md - Task organization includes frontend, backend, DevOps, security phases
- Follow-up items:
  * Update CLAUDE.md runtime guidance to include web-specific patterns
  * Create web-specific code examples in specs/
  * Update existing CLI code contracts to web API contracts
-->

# Full-Stack Todo Web Application Constitution

**Parent Document**: CLI Todo Application Constitution v1.0.0
**Transformation Scope**: CLI Application → Production-Ready Full-Stack Web Application

---

## Document Purpose

This constitution governs the transformation of a CLI Todo application into a **production-ready, professional full-stack web application**. It inherits core principles from the CLI constitution (TDD, separation of concerns, type safety) while introducing comprehensive governance for frontend architecture, backend APIs, web security, deployment, and operational excellence.

---

## 🎯 PART I: INHERITED & ADAPTED PRINCIPLES

The following principles from CLI Todo Constitution v1.0.0 are retained with adaptations for web architecture:

### I. Architecture & Design - Separation of Concerns (ADAPTED)

The application MUST maintain clear boundaries between layers to ensure modularity, testability, and future extensibility.

**Rules:**
- **Frontend ↔ API ↔ Business Logic ↔ Data Layer** MUST be independent layers
- Frontend communicates ONLY via API contracts (no direct database access)
- Each module, class, and function has ONE clear purpose (Single Responsibility Principle)
- Dependencies MUST be passed explicitly via dependency injection; no global state
- Define clear contracts using TypeScript interfaces (frontend), Python Protocols (backend), and OpenAPI schemas (API)
- API routes MUST be thin (validation → delegate to service → return response)
- Business logic MUST live in service layer (testable without HTTP or UI)

**Rationale:** Separation of concerns enables isolated testing, independent frontend/backend development, and the ability to swap implementations (e.g., React → Vue, FastAPI → Django) without cascading changes. This architecture supports long-term maintainability and enables microservices migration if needed.

### II. Code Quality - Explicit & Self-Documenting (RETAINED)

Code clarity and explicit behavior take precedence over cleverness or brevity.

**Rules:**
- Type hints MUST be used everywhere (TypeScript strict mode, Python mypy strict mode)
- Code MUST be self-documenting; avoid magic or implicit behaviors
- DRY (Don't Repeat Yourself) - Extract common patterns, but avoid premature abstraction
- YAGNI (You Aren't Gonna Need It) - Build what's needed now; don't over-engineer
- Fail Fast - Validate inputs early at system boundaries (frontend forms, API gateway, business logic)

**Rationale:** Explicit code reduces cognitive load, makes intent clear to reviewers and future maintainers, and prevents subtle bugs. Type safety catches errors at compile time (TypeScript) and development time (mypy).

### III. Testing - Test-Driven Development (EXPANDED)

Testing is mandatory and MUST follow strict Test-Driven Development (TDD) discipline across frontend, backend, and end-to-end layers.

**Rules:**
- **RED-GREEN-REFACTOR cycle MUST be followed strictly:**
  1. **RED**: Write tests FIRST; verify they FAIL before implementation
  2. **GREEN**: Write minimal code to make tests pass
  3. **REFACTOR**: Clean up code while keeping tests green
- Tests MUST be written BEFORE any implementation code (no exceptions)
- 100% of tests MUST pass before code can be committed or merged
- **Test Pyramid MUST be followed:**
  - **70% Unit Tests**: Functions, classes, components (isolated, fast)
  - **20% Integration Tests**: API endpoints + database, component integration
  - **10% End-to-End Tests**: Full user workflows in browser (Playwright)
- Tests MUST be independent: No shared state or execution order dependencies
- **Coverage requirements:**
  - Backend: Minimum 80% coverage
  - Frontend: Minimum 70% coverage (UI testing more brittle, focus on critical paths)
  - E2E: Must cover all critical user flows (signup → create task → complete task → logout)
- External dependencies (database, network) MUST be mocked in unit tests
- Each test MUST test ONE thing and have a clear, descriptive name

**Frontend Testing:**
- **Unit Tests**: Vitest for components, hooks, utilities
- **Component Tests**: React Testing Library (test user behavior, not implementation)
- **E2E Tests**: Playwright (cross-browser, headless)

**Backend Testing:**
- **Unit Tests**: pytest for services, validators
- **Integration Tests**: pytest with test database (TestContainers for PostgreSQL)
- **API Tests**: pytest + httpx (test FastAPI routes)

**Rationale:** TDD ensures code is testable by design and provides immediate feedback. The test pyramid balances fast feedback (unit tests) with integration confidence (API/E2E tests). Playwright provides cross-browser E2E coverage.

### IV. Data Management - Single Source of Truth (ADAPTED)

Data integrity and consistency are paramount; all data operations must be safe and predictable.

**Rules:**
- One canonical data store: **PostgreSQL** (production) with proper schema design
- All read-modify-write operations MUST be atomic (database transactions)
- Data validation MUST occur at ALL boundaries:
  - Frontend: Client-side validation (React Hook Form + Zod)
  - API: Server-side validation (Pydantic/Zod schemas)
  - Database: Constraints, foreign keys, check constraints
- **Schema versioning MUST use migration tools**: Alembic (Python) or Prisma Migrate (TypeScript)
- Backwards compatibility MUST be maintained; never break existing data (additive changes only)
- **Database design principles:**
  - Follow 3rd Normal Form (3NF) minimum
  - Use UUIDs for primary keys (prevents enumeration attacks)
  - Use indexes for frequently queried columns
  - Use foreign keys to enforce referential integrity

**Rationale:** PostgreSQL provides ACID compliance, JSON support, full-text search, and scalability. Migration tooling prevents schema drift. Validation at multiple layers provides defense in depth. UUIDs improve security.

### V. Error Handling - Clear & User-Friendly (RETAINED)

Errors must be handled gracefully with messages that guide users toward resolution.

**Rules:**
- Define custom exception types for domain-specific errors
- **Frontend errors**: Show user-friendly messages in toast notifications or inline form errors
- **API errors**: Return structured error responses with error codes (never raw exceptions)
- **Backend errors**: Log with full context (request ID, user ID, stack trace) without exposing internals
- Graceful degradation: Handle network failures, timeout errors without crashing
- Every error message MUST be actionable (tell the user what went wrong and how to fix it)

**Error Response Schema (API):**
```json
{
  "error": {
    "code": "TASK_NOT_FOUND",
    "message": "Task with ID 'abc123' does not exist",
    "details": {"task_id": "abc123"},
    "timestamp": "2025-12-19T12:34:56Z",
    "request_id": "req_xyz789"
  }
}
```

**Rationale:** Good error handling distinguishes professional apps from prototypes. Users need clear guidance. Developers need detailed logs. Structured errors enable client-side error handling.

### VI. User Experience - Beautiful & Intuitive Web UI (TRANSFORMED)

The application MUST deliver a production-grade, visually cohesive, accessible web interface.

**Rules:**
- **Design System Consistency:**
  - MUST use centralized design system: Tailwind CSS + Shadcn/ui components
  - Color palette, typography scale, spacing system defined in `tailwind.config.ts`
  - NO arbitrary colors, sizes, or spacing outside design system
- **Visual Hierarchy:**
  - Page titles: `text-3xl font-bold tracking-tight`
  - Section headers: `text-2xl font-semibold`
  - Body text: `text-base`
  - Labels/metadata: `text-sm text-muted-foreground`
- **Interactive States** (MUST be implemented for ALL interactive elements):
  - Hover: `hover:bg-accent transition-colors`
  - Focus: `focus-visible:ring-2 focus-visible:ring-ring`
  - Active: `active:scale-95 transition-transform`
  - Disabled: `disabled:opacity-50 disabled:cursor-not-allowed`
  - Loading: Show skeleton loaders or spinners (never blank states)
- **Empty States**: Show helpful messages with illustration + CTA when no data exists
- **Error States**: Toast notifications (red) for errors, inline errors for form fields
- **Success Feedback**: Toast notifications (green) with auto-dismiss, optimistic UI updates
- **Consistent Feedback**: Every action shows immediate, visible confirmation

**Rationale:** Professional UI generation is the difference between a prototype and a product. Shadcn/ui + Tailwind provide accessible, consistent primitives. Design systems scale across teams and maintain visual consistency.

### VII. Performance & Scalability - Efficient by Design (EXPANDED)

The application must perform efficiently at web scale and be designed for growth.

**Rules:**
- **Frontend Performance:**
  - Code splitting: Use Next.js dynamic imports for heavy components
  - Bundle size: Keep initial JS bundle <200KB gzipped
  - Image optimization: Use Next.js `<Image>` component (automatic WebP, lazy loading)
  - Lazy loading: Defer non-critical components below the fold
- **Backend Performance:**
  - Database query optimization: Use indexes, avoid N+1 queries
  - Caching: Use Redis for frequently accessed data (sessions, task lists)
  - Connection pooling: Use database connection pools (SQLAlchemy pools)
  - Async I/O: Use FastAPI's async endpoints for I/O-bound operations
- **Infrastructure Performance:**
  - CDN: Use Vercel Edge Network or CloudFront for static assets
  - Load balancing: Support horizontal scaling with multiple backend instances
- **Scalability:**
  - MUST handle thousands of concurrent users without degradation
  - Storage layer MUST be pluggable for future migration (PostgreSQL → distributed DB)
  - Use appropriate data structures for O(1) lookups where needed

**Rationale:** Performance directly impacts user experience and SEO. Core Web Vitals affect Google search ranking. These optimizations are proven best practices for production web apps.

### VIII. Security & Safety - Secure by Default (EXPANDED)

Security and data safety must be considered from the start, following OWASP Top 10 guidelines.

**Rules:**
- **Input Validation**: Validate ALL user inputs (frontend + backend)
- **Authentication**: Implement secure authentication (JWT or session-based with HTTP-only cookies)
- **Authorization**: Implement role-based access control (RBAC)
- **Password Security**: Hash passwords with bcrypt/Argon2 (NEVER store plaintext)
- **HTTPS**: Enforce HTTPS in production (TLS 1.3)
- **CORS**: Whitelist allowed origins (NEVER use `*` in production)
- **CSRF**: Implement CSRF tokens for state-changing requests
- **XSS Prevention**: Escape user-generated content, use Content Security Policy (CSP)
- **Rate Limiting**: Limit authentication attempts (5/min), API requests (100/min per user)
- **Dependency Security**: Scan dependencies for vulnerabilities (Dependabot, Snyk)
- **Safe Defaults**: Secure by default; explicit opt-in for risky operations

**Rationale:** Security is non-negotiable for web apps. These measures prevent OWASP Top 10 vulnerabilities (SQL injection, XSS, CSRF, broken authentication). Compliance with security standards protects user data and prevents breaches.

### IX. Python Standards - Modern & Professional (RETAINED for Backend)

Code must follow Python community standards and leverage modern language features.

**Rules:**
- PEP 8 compliance MUST be followed (enforced via tooling)
- Python 3.13+ features MUST be used where appropriate
- Type checking: Run mypy in strict mode (no implicit Any types)
- Linting: Use ruff for fast, comprehensive linting
- Formatting: Use black for consistent, opinionated code formatting
- Dependency management: Use uv for fast, reproducible environments
- All code MUST pass type checking, linting, and formatting checks before commit

**Rationale:** Following Python standards ensures code is familiar to other developers. Modern tooling (ruff, black, mypy, uv) provides fast feedback and catches issues before production.

### X. Development Workflow - Spec-Driven & Systematic (RETAINED)

Development follows a disciplined, spec-driven approach to ensure quality and traceability.

**Rules:**
- Spec-Driven Development MUST be followed: Spec → Plan → Tasks → Implementation
- Small, atomic commits: Each commit represents ONE logical change
- Commit messages MUST follow Conventional Commits format (feat:, fix:, docs:, chore:)
- Branch per feature: Isolated development branches (###-feature-name format)
- Code review ready: All code MUST be self-explanatory or have clear "why" comments
- Every user interaction MUST be recorded in a Prompt History Record (PHR)
- Architecturally significant decisions MUST be documented in Architecture Decision Records (ADRs)

**Rationale:** Spec-driven development prevents scope creep and ensures alignment. Conventional commits enable automated changelog generation. PHRs and ADRs provide project memory and onboarding material.

---

## 🌐 PART II: NEW WEB-SPECIFIC PRINCIPLES

### XI. Frontend Architecture - Professional UI Generation (NON-NEGOTIABLE)

The frontend MUST deliver a production-ready, accessible, responsive user interface using modern React patterns.

**Technology Stack:**
- **Framework**: Next.js 15+ (App Router) with React 19+
- **Styling**: Tailwind CSS 4+ (utility-first design system)
- **Component Library**: Shadcn/ui (accessible primitives)
- **Icons**: Lucide React (consistent iconography)
- **Forms**: React Hook Form + Zod (type-safe validation)
- **State Management**:
  - Server State: TanStack Query (React Query) v5
  - Client State: Zustand (lightweight, TypeScript-first)
- **Type Safety**: TypeScript 5.7+ (strict mode)

**UI Standards:**

**A. Design System Consistency:**
- MUST use centralized `tailwind.config.ts` for colors, typography, spacing
- MUST use Shadcn/ui components for buttons, inputs, dialogs, toasts
- NO arbitrary styles outside design system

**B. Professional UI Generation Rules:**
- **Spacing & Layout**: Container `max-w-7xl`, card padding `p-6`, section gaps `space-y-6`
- **Interactive States**: Hover, focus, active, disabled, loading (see Principle VI)
- **Empty States**: Illustration + descriptive text + CTA button
- **Error/Success Feedback**: Toast notifications with auto-dismiss

**C. Component Patterns:**
- Server Components by default (Next.js App Router)
- Client Components only when needed (interactivity, browser APIs)
- Reusable components in `components/ui/` (Shadcn-generated)
- Feature-specific components in `components/features/`

**Rationale:** Next.js provides server-side rendering, routing, and optimizations. Shadcn/ui provides accessible, customizable components. TanStack Query manages server state efficiently. This stack is production-proven and well-documented.

### XII. API Design & Backend Architecture (NON-NEGOTIABLE)

The backend MUST provide a secure, well-documented RESTful API following industry standards.

**Technology Stack:**
- **Framework**: FastAPI 0.100+ (Python) OR Django 5.0+ (alternative)
- **ORM**: Prisma (TypeScript backend) OR SQLAlchemy 2.0+ (Python backend)
- **Database**: PostgreSQL 16+
- **API Documentation**: OpenAPI 3.1 (auto-generated from FastAPI)
- **Validation**: Pydantic v2 (Python) OR Zod (TypeScript)

**API Design Standards:**

**A. RESTful Principles:**
- **Resource-Oriented URLs**: `/api/v1/tasks`, `/api/v1/tasks/{id}`
- **HTTP Methods**: GET (read), POST (create), PUT (full update), PATCH (partial update), DELETE (delete)
- **Status Codes**: 200 OK, 201 Created, 400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found, 422 Unprocessable Entity, 500 Internal Server Error
- **Pagination**: Use `?page=1&limit=20` or cursor-based for large datasets
- **Filtering/Sorting**: Query params: `?status=completed&sort=-created_at`
- **Versioning**: URL versioning (`/api/v1/`) for breaking changes

**B. Request/Response Schema:**
- MUST define explicit Pydantic/Zod schemas for all request bodies and responses
- MUST validate all inputs at API boundary (fail fast)
- MUST document all schemas in OpenAPI spec

**C. Business Logic Layer:**
- API routes MUST be thin (validation → service → response)
- Business logic MUST live in service layer
- Services MUST be testable without HTTP layer

**Rationale:** RESTful design is industry standard and well-understood. Type-safe schemas prevent runtime errors. OpenAPI enables auto-generated client code. Service layer separation enables testing and reuse.

### XIII. Authentication & Authorization (NON-NEGOTIABLE)

The application MUST implement secure authentication and role-based access control.

**Authentication Strategy:**
- **Recommended**: Session-based (HTTP-only cookies + CSRF protection)
- **Alternative**: JWT (short-lived access tokens + refresh tokens)
- **Optional**: OAuth 2.0 for social login (Google, GitHub)

**Security Requirements:**

**A. Password Security:**
- MUST hash passwords with bcrypt/Argon2
- MUST enforce minimum password strength (8+ chars, mixed case, numbers, symbols)
- MUST implement rate limiting on login (5 failures → 15min lockout)
- MUST support password reset via email with time-limited tokens

**B. Session Management:**
- MUST use HTTP-only, secure cookies (prevents XSS theft)
- MUST implement CSRF protection (double-submit cookie OR synchronizer token)
- MUST expire sessions after inactivity (default: 30 days)

**C. Authorization (RBAC):**
- MUST define roles: `user`, `admin` (expandable)
- MUST enforce role checks in API routes (decorator/middleware)
- MUST implement resource ownership checks (users can only modify their own tasks)

**Rationale:** Authentication is non-negotiable for multi-user apps. Session-based auth is simpler and more secure for traditional web apps. RBAC prevents privilege escalation. These standards follow OWASP best practices.

### XIV. Database Architecture & Migration (NON-NEGOTIABLE)

The application MUST use PostgreSQL with proper schema design and migration tooling.

**Database Selection:**
- **Production**: PostgreSQL 16+ (ACID compliance, JSON support, full-text search)
- **Local Dev**: PostgreSQL via Docker Compose (parity with production)

**Schema Design Principles:**

**A. Normalization:**
- MUST follow 3rd Normal Form (3NF) minimum
- MUST avoid data duplication (use foreign keys)
- MUST use UUIDs for primary keys (prevents enumeration attacks)

**Example Schema:**
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'user',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    status VARCHAR(50) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'completed')),
    priority VARCHAR(50) NOT NULL DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    CONSTRAINT title_length CHECK (char_length(title) >= 1)
);

CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_created_at ON tasks(created_at DESC);
```

**B. Migration Strategy:**
- MUST use migration tools: Alembic (SQLAlchemy) OR Prisma Migrate
- MUST version control all migrations
- MUST write reversible migrations (up + down)
- MUST test migrations on staging before production
- MUST maintain backwards compatibility (additive changes)

**Rationale:** PostgreSQL is industry standard for web apps (ACID, performance, features). UUIDs prevent enumeration attacks. Migration tooling prevents schema drift. Proper indexing ensures query performance.

### XV. Web Security - OWASP Top 10 Compliance (NON-NEGOTIABLE)

The application MUST implement comprehensive security measures following OWASP guidelines.

**Security Measures:**

**A. Input Validation & Sanitization:**
- MUST validate ALL user inputs (frontend + backend)
- MUST sanitize HTML inputs to prevent XSS (use DOMPurify)
- MUST parameterize database queries (ORMs handle this automatically)
- MUST validate file uploads (type, size, content)

**B. XSS Prevention:**
- MUST escape user-generated content when rendering
- MUST use Content Security Policy (CSP) headers
- MUST set `HttpOnly` flag on cookies

**C. CSRF Prevention:**
- MUST implement CSRF tokens for state-changing requests (POST, PUT, DELETE)
- MUST use `SameSite=Lax` or `SameSite=Strict` cookies
- MUST validate Origin/Referer headers

**D. CORS Configuration:**
- MUST whitelist allowed origins (NEVER use `*` in production)
- MUST specify allowed methods and headers
- MUST handle preflight requests (OPTIONS)

**E. Rate Limiting:**
- MUST limit authentication endpoints (5 requests/min per IP)
- MUST limit API endpoints (100 requests/min per user)
- MUST return `429 Too Many Requests` with `Retry-After` header

**F. HTTPS Enforcement:**
- MUST use HTTPS in production (TLS 1.3)
- MUST redirect HTTP → HTTPS (301 Permanent Redirect)
- MUST set `Strict-Transport-Security` header (HSTS)

**Rationale:** These measures prevent the most common web vulnerabilities (OWASP Top 10). HTTPS, CSRF, XSS, rate limiting are standard for production apps. Security is non-negotiable.

### XVI. Accessibility & Responsive Design (NON-NEGOTIABLE)

The application MUST meet WCAG 2.1 AA compliance and work on all device sizes.

**Accessibility Requirements (WCAG 2.1 AA):**

**A. Semantic HTML:**
- MUST use proper HTML elements: `<header>`, `<nav>`, `<main>`, `<article>`, `<button>`
- MUST NOT use `<div onclick>` instead of `<button>`

**B. ARIA Labels:**
- MUST provide accessible names for all interactive elements
- MUST associate labels with form inputs (`htmlFor` attribute)
- MUST provide error descriptions via `aria-describedby`

**C. Keyboard Navigation:**
- MUST support tab order (logical focus flow)
- MUST show visible focus states (`:focus-visible`)
- MUST provide keyboard shortcuts where appropriate

**D. Color Contrast:**
- MUST maintain 4.5:1 ratio for text
- MUST maintain 3:1 ratio for UI components
- MUST NOT rely on color alone (use icons + text)

**E. Screen Reader Support:**
- MUST maintain proper heading hierarchy (H1 → H2 → H3)
- MUST provide skip links
- MUST use live regions for dynamic content

**Responsive Design (Mobile-First):**

**A. Breakpoints:**
- MUST use Tailwind's default breakpoints (sm: 640px, md: 768px, lg: 1024px, xl: 1280px)
- MUST design mobile-first (default styles for mobile, layer on desktop)

**B. Touch Targets:**
- MUST use minimum 44x44px tap targets on mobile

**C. Adaptive Layouts:**
- MUST convert tables to cards/lists on mobile
- MUST use hamburger menu on mobile, horizontal nav on desktop
- MUST test on iOS Safari, Chrome Android

**Rationale:** WCAG compliance is legally required in many jurisdictions and morally correct. Responsive design is mandatory in a mobile-first world (>60% web traffic is mobile). Accessibility improves usability for all users.

### XVII. Deployment & Infrastructure (NON-NEGOTIABLE)

The application MUST be containerized and deployed via automated CI/CD pipelines.

**Containerization (Docker):**

**A. Docker Requirements:**
- MUST containerize frontend, backend, and database
- MUST use multi-stage builds (smaller images, faster deployments)
- MUST use Docker Compose for local development

**Example `docker-compose.yml`:**
```yaml
version: '3.9'
services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: todo_db
      POSTGRES_USER: todo_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: postgresql://todo_user:${DB_PASSWORD}@db:5432/todo_db
      JWT_SECRET: ${JWT_SECRET}
    ports:
      - "8000:8000"
    depends_on:
      - db

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000
    ports:
      - "3000:3000"
    depends_on:
      - backend

volumes:
  postgres_data:
```

**CI/CD Pipeline (GitHub Actions):**

**B. Pipeline Requirements:**
- MUST run on every PR: lint, format, type check, tests, build
- MUST block merge if any step fails
- MUST deploy to staging automatically after merge to `main`
- MUST deploy to production manually (approval required)

**C. Environment Configuration:**
- MUST use environment variables for secrets (NEVER commit secrets)
- MUST use `.env` files for local development (gitignored)
- MUST use secret managers in production (AWS Secrets Manager, Vault)

**D. Deployment Targets:**
- **Recommended**: Vercel (frontend) + Railway/Render (backend + PostgreSQL)
- **Alternative**: AWS (ECS Fargate, RDS, CloudFront)
- **Alternative**: DigitalOcean App Platform (simplest for MVPs)

**Rationale:** Docker ensures parity between local, staging, and production. CI/CD prevents broken code from reaching production. Environment variables keep secrets out of code. These are industry-standard practices.

### XVIII. Monitoring & Observability (NON-NEGOTIABLE)

The application MUST provide structured logging, error tracking, and performance monitoring.

**Logging Requirements:**

**A. Structured Logging:**
- MUST use structured logging (JSON format) for machine parsing
- MUST include context: request ID, user ID, timestamp, log level
- MUST log errors with full stack traces (sanitize sensitive data)

**B. Error Tracking:**
- MUST use error tracking service (Sentry recommended)
- MUST capture unhandled exceptions automatically
- MUST include user context (ID, email) for debugging
- MUST alert on new errors or error spikes

**C. Performance Monitoring:**
- MUST track API response times (p50, p95, p99)
- MUST track database query performance (slow query log)
- MUST track frontend performance (Core Web Vitals: LCP, FID, CLS)

**D. Health Checks:**
- MUST expose `/health` endpoint for uptime monitoring
- MUST check database connectivity, external services

**Example Health Check:**
```python
@app.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")
```

**Rationale:** Production apps need observability to debug issues, track performance, and alert on failures. Structured logging enables log aggregation. Sentry provides actionable error reports. Health checks enable uptime monitoring.

### XIX. Performance Optimization (NON-NEGOTIABLE)

The application MUST implement performance best practices for frontend and backend.

**Frontend Performance:**

**A. Code Splitting:**
- MUST use Next.js dynamic imports for heavy components
- MUST keep initial JS bundle <200KB gzipped

**B. Image Optimization:**
- MUST use Next.js `<Image>` component (automatic WebP, lazy loading, responsive sizes)

**C. Caching:**
- MUST leverage browser caching (Cache-Control headers)
- MUST use CDN for static assets (Vercel Edge, CloudFront)

**D. Prefetching:**
- MUST use Next.js `<Link prefetch>` for instant navigation

**Backend Performance:**

**E. Database Optimization:**
- MUST use indexes for frequently queried columns
- MUST avoid N+1 queries (use `select_related`/`prefetch_related` in ORMs)

**F. Caching:**
- MUST use Redis for frequently accessed data (sessions, task lists)

**G. Connection Pooling:**
- MUST use database connection pools (SQLAlchemy pools)

**H. Async I/O:**
- MUST use async endpoints for I/O-bound operations (database queries, external APIs)

**Rationale:** Performance directly impacts user experience and SEO. Core Web Vitals affect Google search ranking. These optimizations are proven best practices for production web apps.

### XX. Type Safety & API Contracts (NON-NEGOTIABLE)

The application MUST maintain end-to-end type safety between frontend and backend.

**Type Safety Strategy:**

**A. Backend Schemas:**
- MUST define Pydantic schemas for all API request/response types
- MUST auto-generate OpenAPI spec from schemas (FastAPI does this automatically)

**B. Frontend Types:**
- MUST generate TypeScript types from OpenAPI spec
- MUST use generated types in API client code

**Workflow:**
1. Define Pydantic schemas in backend:
   ```python
   class TaskResponse(BaseModel):
       id: str
       title: str
       status: Literal["pending", "completed"]
   ```

2. FastAPI auto-generates OpenAPI spec at `/openapi.json`

3. Generate TypeScript types in frontend:
   ```bash
   npx openapi-typescript http://localhost:8000/openapi.json -o src/types/api.ts
   ```

4. Use generated types:
   ```typescript
   import type { components } from '@/types/api';
   type Task = components['schemas']['TaskResponse'];
   ```

**Benefits:**
- Catch type mismatches at compile time
- Autocomplete for API responses in IDE
- Refactor safely (renaming fields updates frontend automatically)

**Rationale:** Type safety prevents entire classes of bugs. OpenAPI provides machine-readable API documentation and enables code generation. This workflow eliminates manual type synchronization.

---

## 🛠️ PART III: FULL-STACK TOOLING & ENVIRONMENT

### Backend Tooling (Python)

**Mandatory Tools:**
- **Python Version**: 3.13+
- **Dependency Manager**: uv
- **Type Checker**: mypy (strict mode)
- **Linter**: ruff
- **Formatter**: black
- **Framework**: FastAPI 0.100+ OR Django 5.0+
- **ORM**: SQLAlchemy 2.0+ OR Prisma
- **Database**: PostgreSQL 16+
- **Testing**: pytest with pytest-cov
- **API Docs**: OpenAPI 3.1 (auto-generated)

**Installation:**
```bash
# Backend
cd backend
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt

# Run checks
ruff check .
black --check .
mypy .
pytest --cov=src tests/
```

### Frontend Tooling (TypeScript)

**Mandatory Tools:**
- **Node Version**: 20+ LTS
- **Package Manager**: npm OR pnpm
- **Framework**: Next.js 15+ (App Router)
- **Language**: TypeScript 5.7+ (strict mode)
- **Styling**: Tailwind CSS 4+
- **Components**: Shadcn/ui
- **Forms**: React Hook Form + Zod
- **State**: TanStack Query v5 + Zustand
- **Testing**: Vitest + React Testing Library + Playwright
- **Linter**: ESLint
- **Formatter**: Prettier

**Installation:**
```bash
# Frontend
cd frontend
npm install

# Run checks
npm run lint
npm run type-check
npm run test
npm run build
```

### Development Environment

**Required:**
- Docker & Docker Compose (for PostgreSQL)
- Git (version control)
- VSCode OR WebStorm (recommended IDEs)

**Recommended Extensions:**
- ESLint, Prettier, Tailwind CSS IntelliSense (frontend)
- Python, Pylance, Ruff, Black (backend)

---

## 🛡️ PART IV: WEB APPLICATION QUALITY GATES

### Pre-Commit Checklist (Automated via Git Hooks)

**Backend:**
- [ ] All tests pass (pytest)
- [ ] Code coverage ≥80%
- [ ] Linting passes (ruff)
- [ ] Formatting passes (black)
- [ ] Type checking passes (mypy strict)

**Frontend:**
- [ ] All tests pass (Vitest + Playwright)
- [ ] Code coverage ≥70%
- [ ] Linting passes (ESLint)
- [ ] Formatting passes (Prettier)
- [ ] Type checking passes (TypeScript strict)
- [ ] Build succeeds (Next.js build)

**General:**
- [ ] No secrets committed (use git-secrets or gitleaks)
- [ ] Commit message follows Conventional Commits

### Pull Request Checklist (Enforced via CI/CD)

- [ ] All CI checks pass (tests, lint, build)
- [ ] No unresolved merge conflicts
- [ ] Code review approved by at least one team member
- [ ] API changes documented in OpenAPI spec
- [ ] Breaking changes documented in changelog
- [ ] Security implications reviewed (if auth/authz changes)
- [ ] Accessibility tested (keyboard navigation, screen reader)
- [ ] Responsive design tested (mobile, tablet, desktop)
- [ ] Database migrations tested on staging (if schema changes)

### Production Deployment Checklist

- [ ] All staging tests pass
- [ ] Database migrations tested on staging
- [ ] Environment variables configured in production
- [ ] HTTPS configured with valid certificate
- [ ] CORS origins configured (no wildcard `*`)
- [ ] Rate limiting configured
- [ ] Monitoring/alerting configured (Sentry, uptime monitor)
- [ ] Backup strategy in place (database backups)
- [ ] Rollback plan documented

---

## 🚀 PART V: MIGRATION ROADMAP (CLI → FULL-STACK WEB)

### Phase 1: Backend Foundation (Week 1-2)

**Goal**: Establish RESTful API with authentication

1. Set up FastAPI project structure
2. Implement authentication (JWT or session-based)
3. Migrate JSON storage → PostgreSQL with schema
4. Migrate service layer (task_service.py) to work with database
5. Implement RESTful API endpoints (`/api/v1/tasks`)
6. Write API integration tests (pytest + httpx)
7. Set up OpenAPI documentation

**Deliverable**: Working API with authentication, testable via Postman/Swagger

### Phase 2: Frontend Setup (Week 2-3)

**Goal**: Establish Next.js frontend with authentication UI

1. Initialize Next.js project with TypeScript
2. Set up Tailwind CSS + Shadcn/ui components
3. Implement authentication UI (login, signup, password reset)
4. Implement layout (header, navigation, footer)
5. Set up TanStack Query for API data fetching
6. Generate TypeScript types from OpenAPI spec

**Deliverable**: Working authentication flow (login → dashboard)

### Phase 3: Core Features (Week 3-4)

**Goal**: Implement todo CRUD operations

1. Implement task list page (read tasks from API)
2. Implement add task form (with validation)
3. Implement update task modal (edit title, description, priority)
4. Implement delete task confirmation dialog
5. Implement mark task complete/incomplete
6. Add empty states, loading states, error states

**Deliverable**: Full CRUD functionality for tasks

### Phase 4: Testing & Polish (Week 4-5)

**Goal**: Comprehensive testing and UX improvements

1. Write frontend component tests (Vitest + Testing Library)
2. Write E2E tests (Playwright) for critical flows
3. Implement accessibility improvements (WCAG 2.1 AA)
4. Implement responsive design (mobile, tablet, desktop)
5. Performance optimization (bundle size, lazy loading)
6. Add animations and micro-interactions

**Deliverable**: Production-ready UI with tests

### Phase 5: DevOps & Infrastructure (Week 5-6)

**Goal**: Deployment and monitoring

1. Dockerize frontend + backend
2. Set up CI/CD pipeline (GitHub Actions)
3. Deploy to staging environment
4. Set up monitoring (Sentry, uptime monitor)
5. Configure HTTPS, CORS, rate limiting
6. Deploy to production

**Deliverable**: Deployed production app with monitoring

### Phase 6: Iteration & Optimization (Week 6+)

**Goal**: User feedback and improvements

1. Gather user feedback
2. Fix bugs and UX issues
3. Implement advanced features (filters, search, tags)
4. Optimize performance based on metrics
5. Add analytics and user tracking

**Deliverable**: Polished production app with user feedback incorporated

---

## 📋 PART VI: GOVERNANCE

### Amendment Process

This constitution inherits amendment process from CLI constitution v1.0.0 with web-specific additions:

1. Propose changes via issue or discussion with clear rationale
2. Document impact on existing code and practices
3. Update constitution with new version number following semantic versioning:
   - **MAJOR**: Backward-incompatible governance changes (e.g., switching from REST to GraphQL)
   - **MINOR**: New principles added (e.g., adding internationalization requirements)
   - **PATCH**: Clarifications, wording fixes
4. Update all dependent templates (plan, spec, tasks) to reflect changes
5. Migration plan required if existing code must be updated

**Approval Requirements:**
- **PATCH**: Team lead approval
- **MINOR**: Majority approval
- **MAJOR**: Unanimous team consensus

### Compliance Enforcement

- All PRs MUST pass automated checks (CI/CD gates)
- Code review MUST verify architecture compliance (separation of concerns, security)
- Production deployments MUST pass manual security review for auth/authz changes
- Constitution checks are mandatory gates in the planning phase
- Non-compliance blocks merge; no exceptions without explicit documentation

### Conflict Resolution

- If this constitution conflicts with CLI constitution v1.0.0, this document takes precedence for web-specific concerns
- For concerns not covered here (Python standards, TDD discipline), CLI constitution v1.0.0 applies

---

## 🔗 PART VII: REFERENCES

### Parent Documents

- CLI Todo Application Constitution v1.0.0 (inherited principles)
- CLAUDE.md (runtime development guidance for AI agents)

### External Standards

- OWASP Top 10 (web security)
- WCAG 2.1 AA (accessibility)
- OpenAPI 3.1 Specification (API documentation)
- Conventional Commits (commit message format)
- Semantic Versioning (version numbering)

### Technology Documentation

- Next.js: https://nextjs.org/docs
- FastAPI: https://fastapi.tiangolo.com
- Shadcn/ui: https://ui.shadcn.com
- Tailwind CSS: https://tailwindcss.com
- Prisma: https://prisma.io/docs
- Playwright: https://playwright.dev
- TanStack Query: https://tanstack.com/query
- PostgreSQL: https://www.postgresql.org/docs

---

**Version**: 2.0.0
**Parent**: CLI Todo Application Constitution v1.0.0
**Ratified**: 2025-12-19
**Last Amended**: 2025-12-19
**Maintainer**: Saifullah
**Status**: Active
**Scope**: Full-Stack Web Application (Frontend + Backend + Infrastructure)
