# ADR-0001: Full-Stack Architecture Pattern

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-19
- **Feature:** Web Application Conversion (CLI Todo → Full-Stack Web App)
- **Context:** Converting a CLI Python todo application to a full-stack web application requires choosing an architecture pattern. Key constraints: requirement to use Better Auth (JavaScript/TypeScript library), need for REST API, requirement for Neon PostgreSQL, desire to maintain Python familiarity for backend logic.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security?
     2) Alternatives: Multiple viable options considered with tradeoffs?
     3) Scope: Cross-cutting concern (not an isolated detail)?
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

**Adopt a separated full-stack architecture with:**

- **Frontend:** Next.js 16.x (App Router) with TypeScript
- **Backend:** FastAPI (Python) with async SQLModel
- **Authentication:** Better Auth (Next.js API routes) issues JWT tokens
- **Database:** Neon PostgreSQL (shared between Better Auth and FastAPI)
- **Communication:** Frontend → FastAPI via REST API with JWT Bearer tokens
- **Styling:** Tailwind CSS + shadcn/ui
- **Development:** Docker Compose orchestration
- **Ports:** Frontend (3000), Backend (8000)

## Consequences

### Positive

- **Language Flexibility:** Leverage Python expertise for business logic while using JavaScript ecosystem for auth
- **Better Auth Compatibility:** Better Auth works natively in Next.js environment without Python bridges
- **Clear Separation:** Frontend and backend can be developed, tested, and deployed independently
- **Type Safety:** TypeScript frontend + Python type hints provide end-to-end type coverage
- **Async Performance:** FastAPI with async SQLModel enables high-performance database operations
- **Modern DX:** Next.js App Router + FastAPI provide excellent developer experience with hot reload
- **JWT Stateless Auth:** No session storage needed in backend, scales horizontally easily

### Negative

- **Increased Complexity:** Managing two separate services vs monolithic Next.js with API routes
- **CORS Configuration:** Requires explicit CORS setup between frontend and backend
- **Type Synchronization:** Manual effort to keep TypeScript and Python types in sync (no automatic codegen in phase 1)
- **Deployment Overhead:** Two services to deploy and monitor instead of one
- **Auth Token Flow:** Additional complexity in JWT verification on FastAPI side
- **Network Latency:** Inter-service HTTP calls add latency compared to in-process function calls

## Alternatives Considered

### Alternative A: Full Next.js Monolith with API Routes

**Stack:** Next.js 16 with API routes for all backend logic, no separate Python service

**Pros:**
- Single codebase, simpler deployment
- No CORS issues
- Type safety across entire stack
- Better Auth native integration

**Cons:**
- Lose Python familiarity and existing CLI codebase patterns
- Rewrite all business logic in TypeScript
- Cannot reuse existing Python libraries (SQLModel patterns from CLI)

**Why Rejected:** Team has Python expertise and existing CLI patterns worth preserving. Learning curve too steep for timeline.

### Alternative B: FastAPI-Only with Server-Side Rendered Templates

**Stack:** FastAPI with Jinja2 templates, no React/Next.js frontend

**Pros:**
- Single Python service
- Simpler architecture
- No Better Auth integration issues

**Cons:**
- Cannot use Better Auth (requirement violation)
- Poor modern UX compared to React
- Limited frontend interactivity
- Harder to achieve responsive design

**Why Rejected:** Violates Better Auth requirement. Modern web apps benefit from rich client-side interactivity.

### Alternative C: Node.js/Express Backend Instead of FastAPI

**Stack:** Next.js 16 + Express (TypeScript) + Prisma ORM

**Pros:**
- Full JavaScript/TypeScript stack
- Better Auth works natively on both sides
- Easier type sharing
- Single language expertise needed

**Cons:**
- Lose Python expertise and CLI patterns
- Node.js ecosystem less familiar to team
- Would need to learn Prisma instead of SQLModel

**Why Rejected:** Team prefers Python for backend logic. FastAPI provides similar DX to Express with Python benefits.

## References

- Feature Spec: `specs/001-cli-todo/spec.md` (CLI baseline)
- Implementation Plan: To be created in `specs/002-web-app/001-project-setup/`
- Related ADRs: ADR-0002 (API Endpoint Design), ADR-0003 (Environment Config)
- Better Auth Docs: https://www.better-auth.com/docs/
- FastAPI JWT Tutorial: https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/
