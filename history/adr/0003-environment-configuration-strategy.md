# ADR-0003: Environment Configuration Strategy

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-19
- **Feature:** Web Application Conversion (Development Environment Setup)
- **Context:** Need to manage sensitive configuration (database URLs, secret keys, API keys) across frontend and backend services in Docker Compose. Must avoid committing secrets to git while maintaining easy developer onboarding. Team uses monorepo with separate frontend/ and backend/ directories.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security?
     2) Alternatives: Multiple viable options considered with tradeoffs?
     3) Scope: Cross-cutting concern (not an isolated detail)?
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

**Use `env_file` directives in Docker Compose with service-specific .env files:**

**Directory Structure:**
```
hackathon-todo/
├── docker-compose.yml          # Committed to git
├── .gitignore                  # Excludes all .env files
├── frontend/
│   ├── .env.local              # NOT in git (developer creates)
│   ├── .env.example            # Committed template
│   └── ...
└── backend/
    ├── .env                    # NOT in git (developer creates)
    ├── .env.example            # Committed template
    └── ...
```

**docker-compose.yml:**
```yaml
services:
  frontend:
    build: ./frontend
    ports: ["3000:3000"]
    env_file: ./frontend/.env.local

  backend:
    build: ./backend
    ports: ["8000:8000"]
    env_file: ./backend/.env
```

**Environment Files:**

`frontend/.env.example` (committed):
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_SECRET=generate-with-openssl-rand-hex-32
BETTER_AUTH_URL=http://localhost:3000
NODE_ENV=development
```

`backend/.env.example` (committed):
```bash
DATABASE_URL=postgresql://user:pass@ep-xxx.neon.tech/todo_db?sslmode=require
SECRET_KEY=generate-with-openssl-rand-hex-32
CORS_ORIGINS=http://localhost:3000
LOG_LEVEL=INFO
```

**Developer Onboarding:**
1. Clone repository
2. Copy `frontend/.env.example` → `frontend/.env.local`
3. Copy `backend/.env.example` → `backend/.env`
4. Fill in actual secret values (provided separately)
5. Run `docker-compose up`

**Security:**
- `.gitignore` includes `.env` and `.env.local`
- `.env.example` files contain only placeholders, no real secrets
- Real secrets shared via secure channel (password manager, encrypted doc)
- Each developer has their own local `.env` files

## Consequences

### Positive

- **Explicit Configuration:** Each service's env vars clearly defined and scoped
- **Security by Default:** `.env` files in `.gitignore`, can't accidentally commit
- **Simple Mental Model:** One env file per service, obvious location
- **Docker Compose Native:** Uses built-in `env_file` directive, no custom scripts
- **Easy Documentation:** `.env.example` serves as documentation of required vars
- **Developer Friendly:** Copy-paste onboarding, no complex setup
- **Service Isolation:** Frontend and backend env vars don't mix

### Negative

- **Manual Setup Required:** Developers must copy and fill .env files (not automatic)
- **Secret Distribution:** Need out-of-band process to share actual secret values
- **Duplication Risk:** Shared secrets (e.g., `BETTER_AUTH_SECRET`) must be identical in both files
- **No Validation:** Docker Compose doesn't validate env file contents
- **Multiple Files to Maintain:** Two `.env.example` files to keep updated
- **Forgotten Updates:** Easy to forget updating `.env.example` when adding new vars

## Alternatives Considered

### Alternative A: Root-Level .env File

**Pattern:** Single `.env` file in repository root, Docker Compose auto-loads it

**Pros:**
- Single file for all configuration
- Docker Compose auto-loads `.env` from root (no `env_file` needed)
- No duplication of shared secrets
- Simpler for small projects

**Cons:**
- All env vars mixed together (frontend + backend + shared)
- Harder to see which service uses which vars
- Variable name collisions possible
- Less clear separation of concerns
- Scaling to more services becomes messy

**Why Rejected:** Monorepo has clear frontend/backend separation. Configuration should mirror structure. Mixing all vars reduces clarity.

### Alternative B: docker-compose.override.yml

**Pattern:** Main `docker-compose.yml` committed, secrets in `docker-compose.override.yml` (gitignored)

**Pros:**
- Secrets completely separated from main compose file
- Can commit base configuration, override with secrets
- Follows Docker Compose conventions
- Good for multi-environment setups

**Cons:**
- **Two YAML files to maintain** instead of one compose + env files
- YAML syntax more complex than simple key=value
- Less obvious to new developers (where do secrets go?)
- Environment variables still better practice than YAML for config

**Why Rejected:** Added complexity without clear benefit. `.env` files are industry standard for env configuration. Prefer simplicity.

### Alternative C: Environment Variables in docker-compose.yml

**Pattern:** Reference env vars in `docker-compose.yml`, load from system environment

**Config:**
```yaml
services:
  backend:
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - SECRET_KEY=${SECRET_KEY}
```

**Pros:**
- No env_file directive needed
- Explicit in compose file what vars are used
- Can override per deployment

**Cons:**
- **Requires exporting vars in shell** before docker-compose up
- Verbose to list all vars in compose file
- Developer must manually export 10+ variables
- Easy to forget exporting vars, confusing errors
- Doesn't work well in CI/CD without extra scripts

**Why Rejected:** Poor developer experience. Forgetting to export variables causes mysterious failures. `.env` files more ergonomic.

### Alternative D: Secrets Management Service

**Pattern:** Use Vault, AWS Secrets Manager, or similar

**Pros:**
- Centralized secret management
- Audit trail of secret access
- Automatic rotation
- Enterprise-grade security

**Cons:**
- **Massive overkill** for local development
- Requires external service running
- Complex setup for developers
- Additional dependencies
- Network latency to fetch secrets
- Costs money (AWS Secrets Manager)

**Why Rejected:** Over-engineering for hackathon/learning project. Local development doesn't need enterprise secret management.

## References

- Docker Compose Env Files: https://docs.docker.com/compose/environment-variables/set-environment-variables/
- Twelve-Factor App Config: https://12factor.net/config
- Related ADRs: ADR-0001 (Full-Stack Architecture)
- Security Best Practices: https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html
