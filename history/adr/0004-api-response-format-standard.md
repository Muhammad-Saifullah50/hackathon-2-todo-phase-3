# ADR-0004: API Response Format Standard

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-19
- **Feature:** Web Application Conversion (API Response Standards)
- **Context:** Need consistent API response format across all FastAPI endpoints for success and error cases. Frontend developers need predictable structure to handle responses. Must balance between including helpful metadata and keeping responses lean. Team wants explicit status codes in response body in addition to HTTP status headers.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security?
     2) Alternatives: Multiple viable options considered with tradeoffs?
     3) Scope: Cross-cutting concern (not an isolated detail)?
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

**Use consistent JSON envelope with explicit status codes in body:**

**Success Response Structure:**
```json
{
  "status": 200,
  "success": true,
  "data": { ... },
  "message": "Operation completed successfully"
}
```

**Error Response Structure:**
```json
{
  "status": 400,
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid task data",
    "details": { ... }
  }
}
```

**Complete Examples:**

```json
// GET /api/v1/tasks (success)
{
  "status": 200,
  "success": true,
  "data": {
    "tasks": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "title": "Complete project",
        "description": "Finish the web app",
        "status": "pending",
        "created_at": "2025-12-19T10:30:00Z",
        "updated_at": "2025-12-19T10:30:00Z"
      }
    ],
    "total": 1,
    "page": 1,
    "per_page": 10
  },
  "message": "Tasks retrieved successfully"
}

// POST /api/v1/tasks (creation success)
{
  "status": 201,
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "New task",
    "status": "pending",
    "created_at": "2025-12-19T11:00:00Z"
  },
  "message": "Task created successfully"
}

// GET /api/v1/tasks/invalid-id (not found)
{
  "status": 404,
  "success": false,
  "error": {
    "code": "TASK_NOT_FOUND",
    "message": "Task with ID 'invalid-id' not found",
    "details": {
      "task_id": "invalid-id"
    }
  }
}

// POST /api/v1/tasks (validation error)
{
  "status": 400,
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid task data",
    "details": {
      "field_errors": {
        "title": "Title is required"
      }
    }
  }
}

// 401 Unauthorized (no JWT token)
{
  "status": 401,
  "success": false,
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Authentication required",
    "details": {
      "reason": "Missing or invalid JWT token"
    }
  }
}
```

**Implementation:**
- FastAPI sets HTTP status code via `status_code` parameter
- Response body includes same status code for frontend convenience
- All endpoints return JSON (no HTML, XML, or plain text)
- `success` boolean for quick checks
- `message` for user-facing text
- `data` for successful payloads
- `error` object for failures with machine-readable `code`

## Consequences

### Positive

- **Consistency:** All responses follow same structure, easy to document
- **Frontend Convenience:** Status code available in body for debugging without checking headers
- **Type Safety:** Predictable structure enables typed response handlers
- **Error Handling:** Machine-readable error codes enable specific error handling
- **Debugging:** Message field provides human-readable context
- **Extensibility:** Details object allows adding metadata without breaking schema
- **Quick Success Checks:** `success` boolean avoids parsing error objects

### Negative

- **Response Size:** Including status code in body adds redundancy (~15 bytes per response)
- **Envelope Overhead:** Wrapper adds nesting compared to returning data directly
- **Not REST Purist:** True REST responses often return data directly, not enveloped
- **Maintenance:** Must ensure HTTP status and body status always match
- **Extra Typing:** Frontend TypeScript types need to account for envelope
- **Parsing Cost:** Frontend must unwrap `data` property on every success response

## Alternatives Considered

### Alternative A: Industry Standard (No Status in Body)

**Pattern:** Use HTTP status codes only, return data directly on success

**Success:**
```json
{
  "tasks": [...],
  "total": 10
}
```

**Error:**
```json
{
  "error": {
    "code": "TASK_NOT_FOUND",
    "message": "..."
  }
}
```

**Pros:**
- **Industry standard** REST approach
- Smaller response size
- Direct data access (no envelope)
- HTTP status is source of truth

**Cons:**
- Status only in headers (harder to inspect in browser/tools)
- No unified response shape (success vs error structures differ)
- Frontend must check HTTP status separate from body
- Harder to debug in frontend console logs

**Why Rejected:** Team prefers explicit status in body for easier debugging and consistent structure. Slight overhead worth the clarity.

### Alternative B: JSend Format

**Pattern:** Use JSend standard (`status: "success"|"fail"|"error"`)

**Response:**
```json
{
  "status": "success",
  "data": { ... }
}
```

**Pros:**
- Established standard with documentation
- Simple three-state model
- No numeric status in body

**Cons:**
- String status ("success") less precise than numeric (200 vs 201)
- Doesn't distinguish between 200 OK and 201 Created
- Less information available in response body
- Still requires checking HTTP status for details

**Why Rejected:** Numeric status codes provide more precise information. Team wants HTTP status mirrored in body.

### Alternative C: Problem Details (RFC 7807)

**Pattern:** Use RFC 7807 standard for errors

**Error Response:**
```json
{
  "type": "https://api.example.com/errors/task-not-found",
  "title": "Task Not Found",
  "status": 404,
  "detail": "The task with ID 'abc' was not found",
  "instance": "/api/v1/tasks/abc"
}
```

**Pros:**
- Official IETF standard (RFC 7807)
- Rich error metadata
- Includes status code

**Cons:**
- **Only covers errors**, not success responses
- More complex structure than needed
- Requires URLs for error types (extra maintenance)
- Overkill for simple API

**Why Rejected:** Too heavy for hackathon project. Success responses still need separate format. Prefer consistency.

### Alternative D: GraphQL-Style Responses

**Pattern:** Always return 200, embed errors in response

**Response:**
```json
{
  "data": { ... },
  "errors": [...]
}
```

**Pros:**
- Single response structure
- Can return partial data with errors

**Cons:**
- **Violates HTTP semantics** (401 returns 200 status)
- Breaks standard HTTP error handling
- Confusing for monitoring/logging
- Not suitable for REST API

**Why Rejected:** Misuses HTTP status codes. REST APIs should use proper HTTP semantics.

## References

- FastAPI Response Models: https://fastapi.tiangolo.com/tutorial/response-model/
- HTTP Status Codes: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status
- JSend Specification: https://github.com/omniti-labs/jsend
- RFC 7807 Problem Details: https://datatracker.ietf.org/doc/html/rfc7807
- REST API Best Practices: https://restfulapi.net/
- Related ADRs: ADR-0002 (API Endpoint Design)
