# ADR-0002: API Endpoint Design Pattern

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-19
- **Feature:** Web Application Conversion (REST API Design)
- **Context:** Need to design REST API endpoints for a multi-user todo application where users should only access their own tasks. Must decide how to identify users in API requests and structure URL paths. Security is critical - users must not access other users' data.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security?
     2) Alternatives: Multiple viable options considered with tradeoffs?
     3) Scope: Cross-cutting concern (not an isolated detail)?
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

**Use JWT-based user identification with user-agnostic API paths:**

**Endpoint Structure:**
```
GET    /api/v1/tasks              # List current user's tasks
POST   /api/v1/tasks              # Create task for current user
GET    /api/v1/tasks/{task_id}    # Get task (verify ownership)
PUT    /api/v1/tasks/{task_id}    # Update task (verify ownership)
DELETE /api/v1/tasks/{task_id}    # Delete task (verify ownership)
PATCH  /api/v1/tasks/{task_id}/toggle  # Toggle task status
POST   /api/v1/tasks/bulk-toggle  # Bulk status changes
POST   /api/v1/tasks/bulk-delete  # Bulk deletions
GET    /api/v1/health             # Health check (no auth)
```

**Authentication Flow:**
1. Frontend gets JWT token from Better Auth on login
2. Frontend includes JWT in `Authorization: Bearer <token>` header on every request
3. FastAPI middleware extracts and verifies JWT signature
4. Middleware decodes user_id from JWT claims
5. API endpoints automatically filter/validate by authenticated user_id
6. User never appears in URL path

**Security Enforcement:**
- All `/api/v1/tasks*` endpoints require valid JWT token
- Requests without token return `401 Unauthorized`
- User can only see/modify their own tasks (enforced in database queries)
- Task ownership validation on all single-task operations

## Consequences

### Positive

- **Security by Default:** User ID never in URL, can't be manipulated
- **Simple URLs:** Clean, RESTful paths without user context
- **Stateless:** No server-side session storage, scales horizontally
- **Token Expiry:** JWTs auto-expire, forcing re-authentication
- **Standard Practice:** Follows industry-standard OAuth2/JWT patterns
- **Frontend Simplicity:** Client doesn't manage user_id in URLs
- **Middleware Reuse:** Single auth middleware applies to all protected routes

### Negative

- **Token Management:** Frontend must store and attach JWT to every request
- **Token Refresh Complexity:** Need strategy for expired tokens (handled by Better Auth)
- **Debugging Difficulty:** Can't test endpoints in browser without token
- **JWT Verification Overhead:** Every request requires cryptographic signature verification
- **No Token Revocation:** JWTs valid until expiry (can't immediately revoke)
- **Claims Must Stay Small:** JWT size grows with claims, sent on every request

## Alternatives Considered

### Alternative A: User ID in URL Path

**Pattern:** `/api/v1/users/{user_id}/tasks`

**Pros:**
- RESTful resource nesting
- Clear ownership in URL structure
- Easy to test individual user endpoints
- Self-documenting API

**Cons:**
- **Security Risk:** Users could try accessing other user IDs
- Must validate user_id in URL matches JWT user_id on every request
- Verbose URLs
- Frontend must track and inject user_id
- Easy to accidentally expose data if validation missed

**Why Rejected:** Security-first approach. Don't trust URL parameters for user identification. Too easy to make authorization bugs.

### Alternative B: Session-Based Authentication

**Pattern:** Session cookie, user ID stored server-side

**Pros:**
- Server controls sessions, can revoke immediately
- Smaller request size (just session ID cookie)
- Traditional, well-understood pattern

**Cons:**
- **Doesn't work with separated frontend/backend** (CORS complications)
- Requires server-side session storage (Redis/database)
- Doesn't scale horizontally without sticky sessions
- Better Auth uses JWT, not sessions - mismatch
- More complex deployment

**Why Rejected:** Incompatible with Better Auth's JWT approach. Adds state to stateless architecture. Complicates scaling.

### Alternative C: API Keys in Headers

**Pattern:** Custom `X-API-Key` header with user-specific keys

**Pros:**
- Simple to implement
- Long-lived credentials
- Easy to revoke per user

**Cons:**
- No standard for user API keys in web apps
- Key storage on frontend problematic
- No expiration mechanism
- Not compatible with Better Auth
- Reinventing authentication

**Why Rejected:** Better Auth already provides JWT. Don't reinvent authentication when standard exists.

## References

- Feature Spec: `specs/001-cli-todo/spec.md`
- Implementation Plan: To be created
- Related ADRs: ADR-0001 (Full-Stack Architecture)
- FastAPI Security: https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/
- REST API Best Practices: https://restfulapi.net/
- JWT Best Practices: https://datatracker.ietf.org/doc/html/rfc8725
