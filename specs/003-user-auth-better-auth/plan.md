# Implementation Plan: User Authentication (Better Auth)

**Branch**: `004-user-auth-better-auth` | **Date**: 2025-12-19 | **Spec**: [specs/004-user-auth-better-auth/spec.md](spec.md)
**Input**: Feature specification from `/specs/004-user-auth-better-auth/spec.md`

## Summary

Implement a unified authentication system using **Better Auth** in the Next.js frontend and **FastAPI Security** in the backend. The core approach relies on sharing a secret key (`BETTER_AUTH_SECRET`) between both services to sign and verify JWT tokens using the `HS256` algorithm. This enables stateless, secure communication where the backend can independently identify users and enforce data isolation.

## Technical Context

**Language/Version**: Python 3.13, TypeScript (Next.js 15)  
**Primary Dependencies**: `better-auth`, `python-jose[cryptography]`, `fastapi`, `sqlmodel`  
**Storage**: Neon PostgreSQL (shared database)  
**Testing**: `pytest` (backend), `vitest` (frontend)  
**Target Platform**: Linux (Docker Compose)
**Project Type**: Full-stack web application  
**Performance Goals**: JWT verification < 1ms, API response overhead < 5ms  
**Constraints**: Symmetric signing (HS256) requires exact secret match; shared DB requires coordinated schema management.

## Constitution Check

- **Shared Secret Security**: Secret must be managed via `.env` and never committed.
- **Data Isolation**: All backend queries MUST be filtered by `user_id` from JWT.
- **Frontend Protection**: Middleware MUST prevent unauthorized access to `/dashboard`.

## Project Structure

### Documentation (this feature)

```text
specs/004-user-auth-better-auth/
├── plan.md              # This file
├── research.md          # Better Auth and JWT verification research
├── data-model.md        # Updated User shadow model and Better Auth tables
├── quickstart.md        # Setup instructions for auth
└── contracts/
    └── user-me.yaml     # API contract for the /me endpoint
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── config.py        # Add BETTER_AUTH_SECRET validation
│   ├── auth.py          # NEW: JWT verification and Security Dependency
│   ├── models/
│   │   └── user.py      # Update User model to match Better Auth schema
│   └── api/
│       └── routes/
│           └── user.py  # NEW: /me endpoint
└── tests/
    └── unit/
        └── test_auth.py # JWT verification tests

frontend/
├── auth.ts              # NEW: Better Auth server-side config
├── middleware.ts        # NEW: Next.js Auth Guard
├── app/
│   ├── (auth)/          # NEW: Sign-in and Sign-up pages
│   └── dashboard/       # Protected dashboard route
├── lib/
│   ├── auth-client.ts   # NEW: Better Auth client-side config
│   └── api.ts           # Update Axios interceptor for JWT
└── tests/
    └── lib/
        └── api.test.ts  # Interceptor tests
```

**Structure Decision**: Web application structure preserved. Authentication logic introduced as a cross-cutting concern across both frontend and backend.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Shared Database Access | Better Auth requires DB persistence; FastAPI needs user data for relations | External Auth API (e.g. Auth0) adds cost and latency |
| Shadow Model Pattern | FastAPI needs to reference User table for Task relationships | Raw SQL queries reduce type safety and maintainability |
