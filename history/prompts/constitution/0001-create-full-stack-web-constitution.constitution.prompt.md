---
id: 0001
title: Create Full-Stack Web Constitution
stage: constitution
date: 2025-12-19
surface: agent
model: claude-sonnet-4-5
feature: none
branch: master
user: saifullah
command: /sp.constitution
labels: ["constitution", "full-stack", "web-app", "frontend", "backend", "security", "accessibility", "devops"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .specify/memory/constitution.md
tests:
 - null
---

## Prompt

Create a comprehensive full-stack web application constitution that transforms the existing CLI todo app into a production-ready web app.

Key requirements:
- Inherit core principles from existing CLI constitution (TDD, separation of concerns, type safety)
- Add professional UI generation standards (React/Next.js, Tailwind CSS, Shadcn/ui)
- Include modern web architecture (RESTful APIs, authentication, database design)
- Add web security requirements (OWASP Top 10, CORS, CSRF, rate limiting)
- Include deployment and DevOps standards (Docker, CI/CD)
- Add accessibility requirements (WCAG 2.1 AA compliance)
- Include monitoring and observability standards
- Provide migration roadmap from CLI to full-stack web

The constitution should be a safety net for all specs and generated code, ensuring professional, production-ready quality across frontend, backend, and infrastructure.

## Response snapshot

Created comprehensive full-stack web constitution (v2.0.0) that transforms CLI Todo app into production-ready web application:

**PART I: Inherited & Adapted Principles (10 principles)**
- I. Architecture & Design: CLI layers → Web layers (Frontend ↔ API ↔ Services ↔ Database)
- II. Code Quality: Type safety for TypeScript + Python
- III. Testing: Expanded to include E2E (Playwright), test pyramid (70% unit, 20% integration, 10% E2E)
- IV. Data Management: JSON → PostgreSQL with migration tooling (Alembic/Prisma)
- V. Error Handling: Structured error responses for API
- VI. User Experience: CLI UX → Professional Web UI (Next.js/Tailwind/Shadcn)
- VII. Performance: Frontend (bundle size <200KB) + Backend (Redis caching, async I/O)
- VIII. Security: Expanded for OWASP Top 10, HTTPS, CORS, CSRF, rate limiting
- IX. Python Standards: Retained for backend
- X. Development Workflow: Spec-driven approach retained

**PART II: New Web-Specific Principles (10 principles)**
- XI. Frontend Architecture: Next.js 15+ (App Router), Tailwind CSS 4+, Shadcn/ui, TanStack Query v5
- XII. API Design: RESTful standards, FastAPI/Django, OpenAPI 3.1 auto-generation
- XIII. Authentication & Authorization: Session-based (recommended) or JWT, RBAC, password security (bcrypt/Argon2)
- XIV. Database Architecture: PostgreSQL 16+, 3NF normalization, UUIDs, migration tooling
- XV. Web Security: OWASP Top 10 compliance, XSS/CSRF/CORS protection, rate limiting
- XVI. Accessibility & Responsive Design: WCAG 2.1 AA compliance, mobile-first design, semantic HTML
- XVII. Deployment & Infrastructure: Docker containerization, CI/CD (GitHub Actions), environment management
- XVIII. Monitoring & Observability: Structured logging (JSON), Sentry error tracking, health checks
- XIX. Performance Optimization: Code splitting, CDN, Redis caching, database query optimization
- XX. Type Safety & API Contracts: OpenAPI → TypeScript code generation, end-to-end type safety

**PART III: Full-Stack Tooling**
- Backend: Python 3.13+, uv, mypy, ruff, black, FastAPI/Django, SQLAlchemy/Prisma, PostgreSQL 16+, pytest
- Frontend: Node 20+, Next.js 15+, TypeScript 5.7+, Tailwind CSS 4+, Shadcn/ui, TanStack Query, Vitest, Playwright

**PART IV: Quality Gates**
- Pre-commit: All tests pass, coverage thresholds (80% backend, 70% frontend), lint/format/type-check
- Pull request: CI checks, code review, API documentation, security review
- Production deployment: Staging validation, HTTPS, CORS config, monitoring setup

**PART V: Migration Roadmap (6 phases)**
1. Backend Foundation (Week 1-2): FastAPI, auth, PostgreSQL migration, RESTful API
2. Frontend Setup (Week 2-3): Next.js, Tailwind/Shadcn, auth UI, TanStack Query
3. Core Features (Week 3-4): Task CRUD operations, forms, modals, states
4. Testing & Polish (Week 4-5): Component tests, E2E tests, WCAG compliance, responsive design
5. DevOps & Infrastructure (Week 5-6): Docker, CI/CD, staging/production deployment, monitoring
6. Iteration & Optimization (Week 6+): User feedback, performance optimization, advanced features

**PART VI: Governance**
- Amendment process with semantic versioning (MAJOR for breaking changes, MINOR for new principles, PATCH for clarifications)
- Compliance enforcement via automated CI/CD gates
- Conflict resolution with parent CLI constitution

**PART VII: References**
- Parent: CLI Todo Application Constitution v1.0.0
- External standards: OWASP Top 10, WCAG 2.1 AA, OpenAPI 3.1, Conventional Commits
- Technology docs: Next.js, FastAPI, Shadcn/ui, Tailwind, Prisma, Playwright, TanStack Query

## Outcome

- ✅ Impact: Established comprehensive governance for CLI → Full-Stack Web transformation with 20 principles (10 adapted + 10 new), production-ready standards, and 6-phase migration roadmap
- 🧪 Tests: N/A (constitution document)
- 📁 Files: Updated .specify/memory/constitution.md (v1.0.0 → v2.0.0, MAJOR version bump)
- 🔁 Next prompts:
  - Update CLAUDE.md with web-specific runtime guidance (React patterns, API conventions, security practices)
  - Create feature specification for authentication system (user registration, login, password reset)
  - Create feature specification for backend API (RESTful endpoints, OpenAPI docs)
  - Update plan-template.md Constitution Check section with web principles
  - Update spec-template.md to include frontend/backend/infrastructure requirements
  - Update tasks-template.md with frontend/backend/DevOps task phases
- 🧠 Reflection: Constitution successfully transforms CLI governance into comprehensive full-stack web governance. Key additions: professional UI generation standards (Shadcn/Tailwind), web security (OWASP Top 10), accessibility (WCAG 2.1 AA), deployment (Docker/CI/CD), monitoring (Sentry), and type safety (OpenAPI → TypeScript). Migration roadmap provides clear 6-phase transformation path. All principles are declarative, testable, and non-negotiable where appropriate.

## Evaluation notes (flywheel)

- Failure modes observed: None - constitution created successfully on first attempt with comprehensive coverage
- Graders run and results (PASS/FAIL): Manual review - PASS (no unresolved placeholders, all principles declarative and testable, version bump rationale clear)
- Prompt variant (if applicable): Initial full-stack web constitution creation (no variants)
- Next experiment (smallest change to try): Apply web constitution principles during feature specification phase (authentication system, backend API) to validate effectiveness and identify gaps
