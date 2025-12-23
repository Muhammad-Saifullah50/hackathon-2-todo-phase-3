# API Response Format Contract

**Feature**: Project Setup & Architecture
**Branch**: `002-project-setup`
**Created**: 2025-12-19
**Based on**: ADR-0004: Standardized API Response Format

## Overview

This document defines the standardized response format for all API endpoints in the Todo application. Consistent response structures improve client-side error handling, debugging, and API usability.

---

## Response Format Standards

All API responses MUST follow these conventions:

### 1. HTTP Status Codes

Use standard HTTP status codes consistently:

| Status Code | Meaning                  | Usage                                           |
|-------------|--------------------------|-------------------------------------------------|
| 200         | OK                       | Successful GET, PUT, PATCH requests             |
| 201         | Created                  | Successful POST request that creates a resource |
| 204         | No Content               | Successful DELETE request                       |
| 400         | Bad Request              | Invalid request syntax or validation failure    |
| 401         | Unauthorized             | Missing or invalid authentication               |
| 403         | Forbidden                | Authenticated but insufficient permissions      |
| 404         | Not Found                | Resource does not exist                         |
| 409         | Conflict                 | Resource conflict (e.g., duplicate email)       |
| 422         | Unprocessable Entity     | Validation errors (detailed field errors)       |
| 429         | Too Many Requests        | Rate limit exceeded                             |
| 500         | Internal Server Error    | Unexpected server error                         |
| 503         | Service Unavailable      | Service temporarily unavailable (maintenance)   |

### 2. Content-Type

All responses MUST use `Content-Type: application/json` unless explicitly documented otherwise (e.g., file downloads).

### 3. Response Body Structure

All JSON responses MUST follow one of these structures based on the operation type.

---

## Success Response Formats

### Single Resource Response

Used for: GET /resource/:id, POST /resource, PUT /resource/:id, PATCH /resource/:id

```json
{
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "status": "pending",
    "priority": "high",
    "user_id": "650e8400-e29b-41d4-a716-446655440000",
    "created_at": "2025-12-19T12:34:56.789Z",
    "updated_at": "2025-12-19T12:34:56.789Z",
    "completed_at": null
  },
  "meta": {
    "timestamp": "2025-12-19T12:34:56.789Z",
    "request_id": "req_abc123xyz"
  }
}
```

**Structure**:
- `data` (object, required): The resource object
- `meta` (object, optional): Metadata about the request
  - `timestamp` (string, required): ISO 8601 timestamp
  - `request_id` (string, optional): Unique request identifier for debugging

### Collection Response (List)

Used for: GET /resources (with pagination)

```json
{
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Buy groceries",
      "status": "pending",
      "created_at": "2025-12-19T12:34:56.789Z"
    },
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "title": "Finish report",
      "status": "completed",
      "created_at": "2025-12-19T10:00:00.000Z"
    }
  ],
  "meta": {
    "timestamp": "2025-12-19T12:34:56.789Z",
    "request_id": "req_abc123xyz",
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 42,
      "total_pages": 3,
      "has_next": true,
      "has_prev": false
    }
  }
}
```

**Structure**:
- `data` (array, required): Array of resource objects (empty array if no results)
- `meta` (object, required): Metadata
  - `timestamp` (string, required): ISO 8601 timestamp
  - `request_id` (string, optional): Unique request identifier
  - `pagination` (object, required for paginated endpoints): Pagination details
    - `page` (integer, required): Current page number (1-indexed)
    - `limit` (integer, required): Items per page
    - `total` (integer, required): Total number of items across all pages
    - `total_pages` (integer, required): Total number of pages
    - `has_next` (boolean, required): Whether there is a next page
    - `has_prev` (boolean, required): Whether there is a previous page

### Success Response Without Data

Used for: DELETE /resource/:id

```json
{
  "message": "Task deleted successfully",
  "meta": {
    "timestamp": "2025-12-19T12:34:56.789Z",
    "request_id": "req_abc123xyz"
  }
}
```

**Structure**:
- `message` (string, required): Human-readable success message
- `meta` (object, optional): Metadata about the request

---

## Error Response Format

All error responses (4xx, 5xx status codes) MUST follow this structure:

```json
{
  "error": {
    "code": "TASK_NOT_FOUND",
    "message": "Task with ID '550e8400-e29b-41d4-a716-446655440000' does not exist",
    "details": {
      "task_id": "550e8400-e29b-41d4-a716-446655440000"
    }
  },
  "meta": {
    "timestamp": "2025-12-19T12:34:56.789Z",
    "request_id": "req_abc123xyz"
  }
}
```

**Structure**:
- `error` (object, required): Error information
  - `code` (string, required): Machine-readable error code (SCREAMING_SNAKE_CASE)
  - `message` (string, required): Human-readable error message
  - `details` (object, optional): Additional error context
- `meta` (object, optional): Metadata about the request
  - `timestamp` (string, required): ISO 8601 timestamp
  - `request_id` (string, optional): Unique request identifier for debugging

### Validation Error Response (422 Unprocessable Entity)

Used when request validation fails (e.g., missing required fields, invalid formats).

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": {
      "fields": [
        {
          "field": "title",
          "message": "Title is required",
          "code": "REQUIRED_FIELD"
        },
        {
          "field": "priority",
          "message": "Priority must be one of: low, medium, high",
          "code": "INVALID_ENUM",
          "received": "urgent"
        }
      ]
    }
  },
  "meta": {
    "timestamp": "2025-12-19T12:34:56.789Z",
    "request_id": "req_abc123xyz"
  }
}
```

**Validation Error Fields**:
- `fields` (array, required): Array of field-specific errors
  - `field` (string, required): Field name (JSON path for nested fields, e.g., "user.email")
  - `message` (string, required): Human-readable error message
  - `code` (string, required): Machine-readable error code
  - `received` (any, optional): The invalid value that was received

---

## Error Codes Registry

### Authentication Errors (401, 403)

| Error Code              | HTTP Status | Description                                |
|-------------------------|-------------|--------------------------------------------|
| `UNAUTHORIZED`          | 401         | Missing or invalid authentication token    |
| `TOKEN_EXPIRED`         | 401         | Authentication token has expired           |
| `FORBIDDEN`             | 403         | User lacks permission to access resource   |
| `INVALID_CREDENTIALS`   | 401         | Email or password is incorrect             |

### Validation Errors (400, 422)

| Error Code              | HTTP Status | Description                                |
|-------------------------|-------------|--------------------------------------------|
| `VALIDATION_ERROR`      | 422         | Request validation failed (see details)    |
| `BAD_REQUEST`           | 400         | Malformed request syntax                   |
| `REQUIRED_FIELD`        | 422         | Required field is missing                  |
| `INVALID_ENUM`          | 422         | Value not in allowed enum values           |
| `INVALID_FORMAT`        | 422         | Field format is invalid (e.g., email)      |
| `STRING_TOO_SHORT`      | 422         | String length below minimum                |
| `STRING_TOO_LONG`       | 422         | String length exceeds maximum              |

### Resource Errors (404, 409)

| Error Code              | HTTP Status | Description                                |
|-------------------------|-------------|--------------------------------------------|
| `TASK_NOT_FOUND`        | 404         | Task with given ID does not exist          |
| `USER_NOT_FOUND`        | 404         | User with given ID does not exist          |
| `RESOURCE_NOT_FOUND`    | 404         | Generic resource not found                 |
| `DUPLICATE_EMAIL`       | 409         | Email already exists in database           |
| `RESOURCE_CONFLICT`     | 409         | Generic resource conflict                  |

### Server Errors (500, 503)

| Error Code              | HTTP Status | Description                                |
|-------------------------|-------------|--------------------------------------------|
| `INTERNAL_SERVER_ERROR` | 500         | Unexpected server error occurred           |
| `DATABASE_ERROR`        | 500         | Database operation failed                  |
| `SERVICE_UNAVAILABLE`   | 503         | Service temporarily unavailable            |
| `DATABASE_UNAVAILABLE`  | 503         | Database connection failed                 |

### Rate Limiting (429)

| Error Code              | HTTP Status | Description                                |
|-------------------------|-------------|--------------------------------------------|
| `RATE_LIMIT_EXCEEDED`   | 429         | Too many requests, try again later         |

---

## Implementation Examples

### FastAPI Error Response Helper

```python
from fastapi import HTTPException
from datetime import datetime
from typing import Any, Optional
import uuid

class APIError(HTTPException):
    """Base class for API errors with standardized format"""

    def __init__(
        self,
        status_code: int,
        error_code: str,
        message: str,
        details: Optional[dict[str, Any]] = None,
    ):
        self.error_code = error_code
        self.details = details or {}
        super().__init__(
            status_code=status_code,
            detail={
                "error": {
                    "code": error_code,
                    "message": message,
                    "details": self.details,
                },
                "meta": {
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "request_id": f"req_{uuid.uuid4().hex[:12]}",
                },
            },
        )


class TaskNotFoundError(APIError):
    """404 error for missing tasks"""

    def __init__(self, task_id: str):
        super().__init__(
            status_code=404,
            error_code="TASK_NOT_FOUND",
            message=f"Task with ID '{task_id}' does not exist",
            details={"task_id": task_id},
        )


class ValidationError(APIError):
    """422 error for validation failures"""

    def __init__(self, fields: list[dict[str, Any]]):
        super().__init__(
            status_code=422,
            error_code="VALIDATION_ERROR",
            message="Request validation failed",
            details={"fields": fields},
        )
```

### FastAPI Success Response Helper

```python
from typing import Any, Optional
from datetime import datetime
import uuid

def success_response(
    data: Any,
    status_code: int = 200,
    request_id: Optional[str] = None,
) -> dict[str, Any]:
    """Create standardized success response"""
    return {
        "data": data,
        "meta": {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "request_id": request_id or f"req_{uuid.uuid4().hex[:12]}",
        },
    }


def collection_response(
    data: list[Any],
    page: int,
    limit: int,
    total: int,
    request_id: Optional[str] = None,
) -> dict[str, Any]:
    """Create standardized collection response with pagination"""
    total_pages = (total + limit - 1) // limit  # Ceiling division
    return {
        "data": data,
        "meta": {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "request_id": request_id or f"req_{uuid.uuid4().hex[:12]}",
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1,
            },
        },
    }
```

### TypeScript API Client Error Handling

```typescript
// API error types (auto-generated from OpenAPI)
interface APIError {
  error: {
    code: string;
    message: string;
    details?: Record<string, any>;
  };
  meta: {
    timestamp: string;
    request_id?: string;
  };
}

interface APIResponse<T> {
  data: T;
  meta: {
    timestamp: string;
    request_id?: string;
    pagination?: {
      page: number;
      limit: number;
      total: number;
      total_pages: number;
      has_next: boolean;
      has_prev: boolean;
    };
  };
}

// Error handling in API client
import axios, { AxiosError } from 'axios';

export class TodoAPIError extends Error {
  code: string;
  details?: Record<string, any>;
  requestId?: string;
  statusCode: number;

  constructor(error: AxiosError<APIError>) {
    const errorData = error.response?.data?.error;
    super(errorData?.message || 'An unexpected error occurred');
    this.name = 'TodoAPIError';
    this.code = errorData?.code || 'UNKNOWN_ERROR';
    this.details = errorData?.details;
    this.requestId = error.response?.data?.meta?.request_id;
    this.statusCode = error.response?.status || 500;
  }
}

// Usage in API client
export async function getTasks(page: number = 1): Promise<Task[]> {
  try {
    const response = await axios.get<APIResponse<Task[]>>('/api/v1/tasks', {
      params: { page, limit: 20 },
    });
    return response.data.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new TodoAPIError(error);
    }
    throw error;
  }
}

// Error handling in component
try {
  const tasks = await getTasks(1);
} catch (error) {
  if (error instanceof TodoAPIError) {
    switch (error.code) {
      case 'UNAUTHORIZED':
        // Redirect to login
        router.push('/login');
        break;
      case 'RATE_LIMIT_EXCEEDED':
        toast.error('Too many requests. Please try again later.');
        break;
      default:
        toast.error(error.message);
    }
    console.error('Request ID:', error.requestId); // For support tickets
  } else {
    toast.error('An unexpected error occurred');
  }
}
```

---

## Response Headers

### Standard Headers (All Responses)

```
Content-Type: application/json
X-Request-ID: req_abc123xyz
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640000000
```

### Cache Headers (GET Requests)

```
Cache-Control: no-cache, no-store, must-revalidate
Pragma: no-cache
Expires: 0
```

For cacheable resources (future):
```
Cache-Control: public, max-age=3600
ETag: "33a64df551425fcc55e4d42a148795d9f25f89d4"
```

### Security Headers (All Responses)

```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

---

## Compliance Checklist

When implementing any API endpoint, verify:

- [ ] Response status code is appropriate for the operation
- [ ] Response body follows the standardized structure (data/error + meta)
- [ ] Error responses include machine-readable error codes
- [ ] Timestamps are in ISO 8601 format with UTC timezone
- [ ] Request IDs are included for traceability
- [ ] Validation errors include field-level details
- [ ] Error messages are user-friendly (no stack traces or internal details)
- [ ] Standard headers are included (Content-Type, X-Request-ID)
- [ ] OpenAPI spec is updated to reflect the response schema

---

## Example API Endpoints

### GET /api/v1/tasks

**Success Response (200 OK)**:
```json
{
  "data": [
    {"id": "550e8400-...", "title": "Buy groceries", "status": "pending"},
    {"id": "650e8400-...", "title": "Finish report", "status": "completed"}
  ],
  "meta": {
    "timestamp": "2025-12-19T12:34:56.789Z",
    "request_id": "req_abc123xyz",
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 42,
      "total_pages": 3,
      "has_next": true,
      "has_prev": false
    }
  }
}
```

### POST /api/v1/tasks

**Success Response (201 Created)**:
```json
{
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Buy groceries",
    "status": "pending",
    "created_at": "2025-12-19T12:34:56.789Z"
  },
  "meta": {
    "timestamp": "2025-12-19T12:34:56.789Z"
  }
}
```

**Validation Error (422 Unprocessable Entity)**:
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": {
      "fields": [
        {
          "field": "title",
          "message": "Title is required",
          "code": "REQUIRED_FIELD"
        }
      ]
    }
  },
  "meta": {
    "timestamp": "2025-12-19T12:34:56.789Z"
  }
}
```

### GET /api/v1/tasks/:id

**Success Response (200 OK)**:
```json
{
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "status": "pending",
    "user_id": "650e8400-e29b-41d4-a716-446655440000",
    "created_at": "2025-12-19T12:34:56.789Z"
  },
  "meta": {
    "timestamp": "2025-12-19T12:34:56.789Z"
  }
}
```

**Not Found Error (404 Not Found)**:
```json
{
  "error": {
    "code": "TASK_NOT_FOUND",
    "message": "Task with ID '550e8400-e29b-41d4-a716-446655440000' does not exist",
    "details": {
      "task_id": "550e8400-e29b-41d4-a716-446655440000"
    }
  },
  "meta": {
    "timestamp": "2025-12-19T12:34:56.789Z"
  }
}
```

### DELETE /api/v1/tasks/:id

**Success Response (200 OK)**:
```json
{
  "message": "Task deleted successfully",
  "meta": {
    "timestamp": "2025-12-19T12:34:56.789Z"
  }
}
```

---

## Summary

This API response format contract ensures:

- **Consistency**: All endpoints follow the same structure
- **Debuggability**: Request IDs enable tracing through logs
- **Client-Friendly**: Machine-readable error codes enable specific error handling
- **Standards-Compliant**: Follows REST API best practices
- **Type-Safe**: Enables TypeScript type generation from OpenAPI spec

All backend implementations MUST adhere to this contract to maintain API consistency.
