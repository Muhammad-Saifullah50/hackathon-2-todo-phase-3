# Refactoring Plan - Security & Code Quality Fixes

**Date:** 2026-01-02
**Status:** Ready to Execute
**Test Coverage:** Critical modules at 95-100% ✅

---

## ✅ What's Protected (Safe to Refactor)

These modules have comprehensive test coverage and can be safely refactored:

| Module | Coverage | Tests | Status |
|--------|----------|-------|--------|
| **auth.py** | 100% | 24 tests | ✅ FULLY PROTECTED |
| **task_service.py** | 97.02% | 74 tests | ✅ FULLY PROTECTED |
| **recurring_service.py** | 98.21% | 33 tests | ✅ FULLY PROTECTED |
| **All models** | 100% | Multiple | ✅ FULLY PROTECTED |
| **All schemas** | 90%+ | Multiple | ✅ FULLY PROTECTED |
| **subtask_service.py** | 93.91% | Multiple | ✅ PROTECTED |
| **tag_service.py** | 85.45% | Multiple | ✅ PROTECTED |

**Total Safety Net:** 430+ tests, all passing

---

## 🔴 Phase 1: CRITICAL Security Fixes (DO FIRST)

### 1. Add Authentication to MCP Server ⚠️ CRITICAL

**Priority:** URGENT
**Risk Level:** CRITICAL - Anyone can access/modify any user's tasks
**Estimated Time:** 45 minutes
**Test Coverage:** None (MCP server has 0% coverage)

**Current Issue:**
```python
# mcp_server/main.py:130, 225, 290, 331, 365, 371
async def add_task(
    title: str,
    user_id: str = "default_user",  # ❌ Hardcoded! No authentication!
):
```

**Impact:**
- Unauthenticated access to all user data
- Anyone can create/read/update/delete tasks for any user
- Major security vulnerability

**Fix:**
```python
# Add JWT authentication to MCP tools
async def add_task(
    title: str,
    authorization: str,  # ✓ Require JWT token
):
    # Verify JWT and extract user_id
    user = await verify_jwt_token(authorization)
    # Use authenticated user_id
    ...
```

**Steps:**
1. Add JWT verification to MCP server
2. Require Authorization header for all MCP tools
3. Extract user_id from verified token
4. Remove hardcoded `user_id="default_user"`
5. Test with real JWT tokens
6. Update MCP client to pass Authorization header

**Files to Modify:**
- `mcp_server/main.py` (lines 130, 225, 290, 331, 365, 371)
- Add new `mcp_server/auth.py` for JWT verification

---

### 2. Implement Rate Limiting ⚠️ HIGH

**Priority:** HIGH
**Risk Level:** HIGH - Vulnerable to DoS attacks
**Estimated Time:** 30 minutes
**Test Coverage:** Can test after implementation

**Current Issue:**
- No rate limiting on any endpoints
- Attackers can spam requests
- Can exhaust server resources

**Impact:**
- Denial of Service (DoS) attacks
- Server overload
- Increased costs
- Poor user experience during attacks

**Fix:**
```python
# backend/src/main.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Apply to routes
@router.post("/api/v1/tasks/")
@limiter.limit("100/minute")  # 100 requests per minute per IP
async def create_task(...):
    ...
```

**Steps:**
1. Install `slowapi` package
2. Configure rate limiter in `main.py`
3. Add rate limits to all public endpoints:
   - Authentication: 5/minute
   - Task CRUD: 100/minute
   - Search: 60/minute
   - Bulk operations: 20/minute
4. Add custom rate limit headers
5. Document rate limits in API docs
6. Test with ab (Apache Bench) or locust

**Files to Modify:**
- `backend/pyproject.toml` (add slowapi dependency)
- `backend/src/main.py` (configure limiter)
- `backend/src/api/routes/*.py` (add @limiter.limit decorators)

---

### 3. Fix CORS Configuration ⚠️ HIGH

**Priority:** HIGH
**Risk Level:** HIGH - CSRF attacks possible
**Estimated Time:** 5 minutes
**Test Coverage:** ✅ Protected (auth.py 100%)

**Current Issue:**
```python
# mcp_server/main.py:69
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ❌ Allows ANY origin!
    allow_credentials=True,
)
```

**Impact:**
- Cross-Site Request Forgery (CSRF) attacks
- Malicious sites can make requests on behalf of users
- Data theft possible

**Fix:**
```python
# For production
ALLOWED_ORIGINS = [
    "https://yourapp.com",
    "https://www.yourapp.com",
]

# For development
if settings.ENVIRONMENT == "development":
    ALLOWED_ORIGINS.extend([
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ])

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # ✓ Specific domains only
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["*"],
)
```

**Steps:**
1. Add `ALLOWED_ORIGINS` to environment variables
2. Update CORS configuration in both backend and MCP server
3. Test from allowed origin (should work)
4. Test from disallowed origin (should fail)
5. Document CORS policy

**Files to Modify:**
- `mcp_server/main.py:69`
- `backend/src/config.py` (add ALLOWED_ORIGINS setting)
- `backend/src/main.py` (if CORS is configured there)
- `.env.example` (document new env var)

---

### 4. Remove Debug Logging ⚠️ HIGH

**Priority:** HIGH
**Risk Level:** HIGH - Exposes sensitive data
**Estimated Time:** 5 minutes
**Test Coverage:** ✅ Protected (auth.py 100%)

**Current Issue:**
```python
# backend/src/auth.py:142-144
print(f"JWT verification error: {e}")  # ❌ Prints sensitive data
print(f"Public Key used: {public_key_data}")  # ❌ Exposes keys
print(f"Token (first 50 chars): {token.credentials[:50]}")  # ❌ Exposes tokens
```

**Impact:**
- JWT tokens logged to stdout
- Public keys exposed in logs
- Attackers can extract tokens from logs
- Compliance violations (logging sensitive data)

**Fix:**
```python
# Remove print statements entirely, or replace with proper logging
logger.debug("JWT verification failed", extra={
    "error_type": type(e).__name__,
    # Don't log actual tokens or keys!
})
```

**Steps:**
1. Remove all `print()` statements from `auth.py`
2. Use `logger.debug()` for development debugging
3. Ensure logger is configured to NOT log to stdout in production
4. Search for other print statements: `grep -r "print(" src/`
5. Remove or replace all debugging prints

**Files to Modify:**
- `backend/src/auth.py:142-144`

---

### 5. Fix JWT Key Caching ⚠️ MEDIUM-HIGH

**Priority:** MEDIUM-HIGH
**Risk Level:** MEDIUM - Key rotation won't work
**Estimated Time:** 15 minutes
**Test Coverage:** ✅ Protected (auth.py 100%)

**Current Issue:**
```python
# backend/src/auth.py:51-55
_public_key_cache = None

async def get_public_key():
    global _public_key_cache
    if _public_key_cache is not None:
        return _public_key_cache  # ❌ Cached forever!

    # Fetch key...
    _public_key_cache = key  # ❌ Never invalidated!
    return key
```

**Impact:**
- Key rotation doesn't work without server restart
- Old keys remain valid indefinitely
- Security vulnerability if key is compromised
- Can't revoke access properly

**Fix:**
```python
import time
from typing import Optional, Tuple

_public_key_cache: Optional[Tuple[str, float]] = None
CACHE_TTL = 3600  # 1 hour

async def get_public_key():
    global _public_key_cache

    # Check if cache is valid
    if _public_key_cache is not None:
        key, timestamp = _public_key_cache
        if time.time() - timestamp < CACHE_TTL:
            return key

    # Fetch new key
    key = await fetch_public_key_from_clerk()
    _public_key_cache = (key, time.time())
    return key
```

**Steps:**
1. Add TTL-based cache expiration (1 hour)
2. Store timestamp with cached key
3. Check cache age before returning
4. Refetch if expired
5. Add tests for cache expiration
6. Consider using Redis for multi-instance deployments

**Files to Modify:**
- `backend/src/auth.py:51-55`

---

### 6. Remove Security Middleware Monkey Patch ⚠️ HIGH

**Priority:** HIGH
**Risk Level:** HIGH - DNS rebinding attacks possible
**Estimated Time:** 20 minutes
**Test Coverage:** None (MCP server has 0% coverage)

**Current Issue:**
```python
# mcp_server/main.py:467-481
def _patched_validate_host(self, host):
    """Allow all hosts for Vercel deployment"""
    return True  # ❌ Disables ALL host validation!

TransportSecurityMiddleware._validate_host = _patched_validate_host  # ❌ Monkey patch!
```

**Impact:**
- DNS rebinding attacks possible
- Host header injection attacks
- Complete bypass of security middleware
- Vercel deployment doesn't require this!

**Fix:**
```python
# Proper host validation
ALLOWED_HOSTS = [
    "yourapp.vercel.app",
    "api.yourapp.com",
    "localhost",  # For development
]

if settings.ENVIRONMENT == "development":
    ALLOWED_HOSTS.append("127.0.0.1")

# Configure middleware properly instead of monkey patching
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=ALLOWED_HOSTS
)

# Remove monkey patch entirely!
```

**Steps:**
1. Remove monkey patch code (lines 467-481)
2. Add proper `ALLOWED_HOSTS` configuration
3. Use built-in `TrustedHostMiddleware` instead
4. Test with valid hosts (should work)
5. Test with invalid hosts (should reject)
6. Document allowed hosts in deployment guide

**Files to Modify:**
- `mcp_server/main.py:467-481` (REMOVE entirely)
- `mcp_server/config.py` (add ALLOWED_HOSTS)

---

## 🟡 Phase 2: Code Quality Fixes (DO NEXT)

### 7. Fix Port Configuration Mismatch

**Priority:** MEDIUM
**Estimated Time:** 5 minutes

**Current Issue:**
- Backend runs on port 9000
- Frontend expects port 8000

**Fix:**
```python
# Option 1: Change backend to 8000
# backend/src/main.py:78
uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)

# Option 2: Update frontend to expect 9000
# frontend/lib/api.ts:4
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:9000';
```

**Files to Modify:**
- `backend/src/main.py:78` OR `frontend/lib/api.ts:4`
- Update documentation to match

---

### 8. Add Database Indexes

**Priority:** MEDIUM
**Estimated Time:** 20 minutes
**Test Coverage:** ✅ Protected (models 100%)

**Current Issue:**
- Missing composite index on `(user_id, deleted_at)`
- Slow queries when filtering by user and excluding deleted

**Fix:**
```sql
-- Create Alembic migration
-- alembic/versions/xxx_add_composite_indexes.py

def upgrade():
    op.create_index(
        'idx_tasks_user_deleted',
        'tasks',
        ['user_id', 'deleted_at'],
        postgresql_where=sa.text('deleted_at IS NULL')
    )

def downgrade():
    op.drop_index('idx_tasks_user_deleted', table_name='tasks')
```

**Steps:**
1. Create Alembic migration
2. Add composite indexes:
   - `tasks(user_id, deleted_at)`
   - `tags(user_id, name)` (for uniqueness check)
   - `task_tags(task_id, tag_id)` (if missing)
3. Test migration up/down
4. Verify query performance improvement
5. Apply to production

**Files to Create:**
- New Alembic migration file

---

### 9. Fix Memory Leak in Optimistic Updates

**Priority:** MEDIUM
**Estimated Time:** 30 minutes
**Test Coverage:** ⚠️ Partial (frontend needs more tests)

**Current Issue:**
```typescript
// frontend/hooks/useTasks.ts:51-86
const tempId = `temp-${crypto.randomUUID()}`;

queryClient.setQueryData(['tasks'], (old) => ({
  ...old,
  tasks: [...old.tasks, { id: tempId, ...newTask }]
}));

// If mutation fails, temp task remains! ❌
```

**Impact:**
- Failed task creations leave ghost tasks in UI
- Memory leak with accumulating temporary tasks
- Confusing UX

**Fix:**
```typescript
onMutate: async (newTask) => {
  await queryClient.cancelQueries({ queryKey: ['tasks'] });
  const previousTasks = queryClient.getQueryData(['tasks']);
  const tempId = `temp-${crypto.randomUUID()}`;

  queryClient.setQueryData(['tasks'], (old) => ({
    ...old,
    tasks: [...old.tasks, { id: tempId, ...newTask }]
  }));

  return { previousTasks, tempId };  // ✓ Return tempId
},

onError: (err, variables, context) => {
  // ✓ Rollback removes temp task
  queryClient.setQueryData(['tasks'], context.previousTasks);
  toast.error('Failed to create task');
},
```

**Steps:**
1. Update optimistic update logic
2. Properly clean up temporary IDs on error
3. Add tests for error scenarios
4. Test with network failures
5. Verify no ghost tasks remain

**Files to Modify:**
- `frontend/hooks/useTasks.ts:51-86`

---

### 10. Standardize Error Response Format

**Priority:** MEDIUM
**Estimated Time:** 45 minutes
**Test Coverage:** ⚠️ Partial (API routes 36-49%)

**Current Issue:**
- Some endpoints return `{success: false, error: {...}}`
- Others return `{detail: "..."}`
- Inconsistent error handling in frontend

**Impact:**
- Frontend must handle multiple error formats
- Difficult to show consistent error messages
- Poor developer experience

**Fix:**
```python
# Create standardized error response
from src.schemas.responses import StandardizedResponse

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content=StandardizedResponse(
            success=False,
            message=exc.detail.get("message", str(exc.detail)),
            error={
                "code": exc.detail.get("code", "ERROR"),
                "details": exc.detail.get("details", None)
            }
        ).model_dump()
    )
```

**Steps:**
1. Create global exception handler
2. Standardize all error responses
3. Update API routes to use standard format
4. Update frontend error handling
5. Document error response format
6. Test all error scenarios

**Files to Modify:**
- `backend/src/main.py` (add exception handler)
- All `backend/src/api/routes/*.py` (standardize errors)
- Frontend error handling code

---

### 11. Add Input Sanitization (XSS Prevention)

**Priority:** MEDIUM
**Estimated Time:** 30 minutes
**Test Coverage:** ✅ Protected (models 100%)

**Current Issue:**
- User-generated content (notes, descriptions) not sanitized
- If rendered as HTML, XSS attacks possible

**Impact:**
- Stored XSS vulnerability
- Attackers can inject malicious scripts
- Steal user data, session tokens

**Fix:**
```python
import bleach

# Add sanitization to models or service layer
def sanitize_html(text: str) -> str:
    """Remove dangerous HTML/JS from user input."""
    if not text:
        return text

    return bleach.clean(
        text,
        tags=['b', 'i', 'u', 'em', 'strong', 'a', 'p', 'br'],
        attributes={'a': ['href', 'title']},
        strip=True
    )

# Apply before saving
task.description = sanitize_html(task_data.description)
```

**Steps:**
1. Install `bleach` package
2. Add sanitization function
3. Apply to all user text fields:
   - Task title, description, notes
   - Tag names
   - Template names/descriptions
4. Add tests for XSS attempts
5. Consider Content-Security-Policy headers

**Files to Modify:**
- `backend/pyproject.toml` (add bleach)
- `backend/src/services/task_service.py`
- Other services with user input

---

## 🟢 Phase 3: Architecture Improvements (OPTIONAL)

### 12. Improve Type Safety in Frontend

**Priority:** LOW
**Estimated Time:** 2 hours

**Current Issue:**
```typescript
// frontend/hooks/useTasks.ts:58
queryClient.setQueryData(tasksKeys.all, (old: any) => {  // ❌ any type
```

**Fix:**
```typescript
interface TasksQueryData {
  data: {
    tasks: Task[];
    metadata: TaskMetadata;
  };
}

queryClient.setQueryData<TasksQueryData>(tasksKeys.all, (old) => {
```

---

### 13. Add React Error Boundary

**Priority:** LOW
**Estimated Time:** 30 minutes

**Current Issue:**
- No global error boundary
- Uncaught errors crash entire app

**Fix:**
```tsx
// app/error-boundary.tsx
'use client';

export default function ErrorBoundary({ error, reset }) {
  return (
    <div>
      <h2>Something went wrong!</h2>
      <button onClick={() => reset()}>Try again</button>
    </div>
  );
}
```

---

### 14. Implement Connection Pooling

**Priority:** LOW
**Estimated Time:** 15 minutes

**Current Issue:**
- No visible connection pool configuration
- May exhaust database connections under load

**Fix:**
```python
# backend/src/db/session.py
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=20,        # Max connections
    max_overflow=10,     # Extra connections if needed
    pool_timeout=30,     # Wait time for connection
    pool_pre_ping=True,  # Test connections before use
)
```

---

## 📋 Execution Order (Recommended)

### Week 1: Critical Security (2-3 hours)
1. ✅ Remove debug logging (5 min)
2. ✅ Fix CORS configuration (5 min)
3. ✅ Fix port mismatch (5 min)
4. ✅ Fix JWT key caching (15 min)
5. ✅ Remove security monkey patch (20 min)
6. ✅ Implement rate limiting (30 min)
7. ✅ Add MCP authentication (45 min)

**Total: ~2 hours**

### Week 2: Code Quality (2-3 hours)
8. Add database indexes (20 min)
9. Fix memory leak in optimistic updates (30 min)
10. Standardize error responses (45 min)
11. Add input sanitization (30 min)

**Total: ~2 hours**

### Week 3+: Architecture (Optional)
12. Improve type safety
13. Add error boundary
14. Connection pooling
15. Add frontend tests

---

## ⚠️ Important Notes

### Before Starting:
1. ✅ **Run all tests:** `uv run pytest` (should pass)
2. ✅ **Create feature branch:** `git checkout -b security-fixes`
3. ✅ **Commit after each fix** (not all at once)
4. ✅ **Test after each change**

### During Refactoring:
- Run tests after EACH change
- If tests fail, fix immediately
- Don't move to next item until current one passes
- Document any issues encountered

### After Completion:
- Run full test suite
- Test manually in browser
- Review all changes
- Create PR with detailed description
- Deploy to staging first

---

## 🎯 Success Criteria

**Security Fixes Complete When:**
- ✅ All 7 critical security issues resolved
- ✅ All 430+ tests still passing
- ✅ Manual testing confirms fixes work
- ✅ No new security vulnerabilities introduced
- ✅ Documentation updated

**Code Quality Complete When:**
- ✅ All 4 code quality issues resolved
- ✅ Tests still passing
- ✅ Performance improved (measure query times)
- ✅ Error handling consistent

---

## 📊 Risk Assessment

### Low Risk (Safe to do now):
- Remove debug logging ✅
- Fix CORS ✅
- Fix port mismatch ✅
- Fix JWT caching ✅

### Medium Risk (Test thoroughly):
- Rate limiting (may need tuning)
- MCP authentication (major change)
- Error standardization (affects all endpoints)

### High Risk (Proceed carefully):
- Remove security monkey patch (may break deployment)
- Database indexes (test rollback)

---

## 🔄 Rollback Plan

If anything breaks:

```bash
# Rollback last commit
git reset --hard HEAD~1

# Or revert specific commit
git revert <commit-hash>

# Run tests to verify
uv run pytest

# If database migration breaks
cd backend && alembic downgrade -1
```

Keep each fix in separate commits for easy rollback!

---

**Ready to start? Begin with Phase 1, item #1: Remove debug logging (easiest, safest)**
