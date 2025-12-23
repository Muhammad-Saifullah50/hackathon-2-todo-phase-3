# Research: User Authentication (Better Auth)

This document explores the technical details for integrating Better Auth into the Next.js frontend and FastAPI backend.

## 1. Better Auth (Frontend)

Better Auth is a framework-agnostic authentication library for TypeScript. In this project, it will run as Next.js API routes.

### Configuration (`frontend/auth.ts`)
- **Adapter**: Uses `better-auth/adapters/prisma` or `better-auth/db` (PostgreSQL adapter).
- **Plugins**: Must enable the `jwt` plugin to issue tokens for the backend.
- **Environment Variables**:
  - `BETTER_AUTH_SECRET`: Used for signing sessions and JWTs.
  - `BETTER_AUTH_URL`: The base URL of the auth endpoints.

### JWT Plugin Details
The `jwt` plugin allows issuing self-contained tokens that can be verified by the FastAPI backend without querying the session database.
- **Algorithm**: `HS256` (Symmetric signing using the shared secret).
- **Claims**: `sub` (User UUID), `email`, `name`.
- **Custom Claims**: Can be added via the plugin configuration if needed.

### Client-Side Integration
- `authClient`: Used for `signIn.email()`, `signUp.email()`, and `signOut()`.
- **Token Retrieval**: The client can retrieve the JWT via `authClient.jwt.generate()` or similar (Better Auth handles session-to-JWT conversion).

## 2. FastAPI (Backend)

The backend needs to verify the JWT issued by Better Auth.

### JWT Verification (`python-jose`)
- **Secret**: Must use the same `BETTER_AUTH_SECRET` as the frontend.
- **Algorithm**: `HS256`.
- **Validation**:
  - `exp`: Token must not be expired.
  - `iss`: Validate against "todo-auth" (configured in Better Auth).
  - `aud`: Validate against "todo-api" (configured in Better Auth).
  - `sub`: Extract as the internal User ID.

### Dependency Injection
A security dependency will be implemented:
```python
async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    # verify and decode token
    # return user or raise 401
```

## 3. Database Strategy

Both services share the same Neon PostgreSQL database.

### Table Ownership
- **Better Auth Tables**: `user`, `session`, `account`, `verification`. Managed by Better Auth.
- **App Tables**: `task`. Managed by Alembic.

### Shadow Model (SQLModel)
The `User` model in FastAPI will map to the existing `user` table created by Better Auth.
- **Alembic Configuration**: Use `include_object` in `env.py` to ignore Better Auth internal tables during migrations.

## 4. Integration Logic

1. **Signup/Login**: User interacts with Next.js frontend → Better Auth creates records in DB.
2. **API Call**: Frontend Axios interceptor gets JWT from Better Auth → Adds `Authorization: Bearer <token>` header.
3. **Backend Processing**: FastAPI extracts `sub` from JWT → Uses it to filter `Task` queries.

## 5. Security Considerations
- **Secret Management**: `BETTER_AUTH_SECRET` must be high entropy and stored securely.
- **CORS**: FastAPI must allow the frontend origin.
- **HTTPS**: Required for secure cookie handling and token transmission in production.
