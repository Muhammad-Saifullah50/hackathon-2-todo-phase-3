# Quickstart Guide: Todo Application

**Feature**: Project Setup & Architecture
**Branch**: `002-project-setup`
**Last Updated**: 2025-12-19

## Overview

This guide helps developers set up the Todo application development environment in under 10 minutes. The application uses a monorepo structure with Next.js frontend, FastAPI backend, and Neon PostgreSQL database.

---

## Prerequisites

Before starting, ensure you have the following installed:

### Required Software

| Software        | Version      | Check Command         | Installation Guide                              |
|-----------------|--------------|------------------------|------------------------------------------------|
| Docker          | 20.10+       | `docker --version`     | https://docs.docker.com/get-docker/            |
| Docker Compose  | 2.0+         | `docker-compose --version` | Included with Docker Desktop                   |
| Node.js         | 22.x LTS     | `node --version`       | https://nodejs.org/ or use nvm                 |
| npm             | 10.x         | `npm --version`        | Included with Node.js                          |
| Python          | 3.13+        | `python --version`     | https://www.python.org/downloads/              |
| uv              | Latest       | `uv --version`         | `pip install uv`                               |
| Git             | 2.x          | `git --version`        | https://git-scm.com/downloads                  |

### Optional (Recommended)

- **Visual Studio Code** with extensions:
  - ESLint
  - Prettier
  - Tailwind CSS IntelliSense
  - Python
  - Pylance
  - Ruff

- **Database Client** (for inspecting PostgreSQL):
  - pgAdmin: https://www.pgadmin.org/
  - DBeaver: https://dbeaver.io/
  - TablePlus: https://tableplus.com/

### Neon PostgreSQL Account

Sign up for a free Neon account: https://neon.tech/

---

## Quick Setup (TL;DR)

For experienced developers, here's the shortest path:

```bash
# Clone repository
git clone <repository-url>
cd hackathon-2-todo-phase-2

# Configure environment variables
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local
# Edit .env files with your Neon database credentials

# Start services with Docker Compose
docker-compose up

# Access application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

---

## Detailed Setup Instructions

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd hackathon-2-todo-phase-2
```

Verify the directory structure:
```bash
ls -la
# You should see: backend/, frontend/, docker-compose.yml, README.md
```

---

### Step 2: Set Up Neon PostgreSQL Database

1. **Sign up for Neon**: https://neon.tech/

2. **Create a new project**:
   - Click "New Project"
   - Name: `todo-app-dev`
   - Region: Choose closest to your location
   - PostgreSQL version: 16

3. **Get the connection string**:
   - Navigate to "Dashboard" → "Connection Details"
   - Copy the connection string (it looks like this):
     ```
     postgresql://user:password@ep-cool-name-123456.us-east-2.aws.neon.tech/neondb?sslmode=require
     ```

4. **Save the connection string** (you'll need it in the next step)

---

### Step 3: Configure Environment Variables

#### Backend Configuration

```bash
cd backend
cp .env.example .env
```

Edit `backend/.env` with your favorite editor:

```bash
# backend/.env
DATABASE_URL=postgresql://your-user:your-password@your-host.neon.tech/neondb?sslmode=require
SECRET_KEY=your-random-secret-key-here-generate-with-openssl
CORS_ORIGINS=["http://localhost:3000"]
LOG_LEVEL=DEBUG
```

**Generate a secure SECRET_KEY**:
```bash
# On macOS/Linux
openssl rand -hex 32

# On Windows (PowerShell)
-join (1..32 | ForEach-Object { '{0:x}' -f (Get-Random -Maximum 256) })
```

#### Frontend Configuration

```bash
cd ../frontend
cp .env.example .env.local
```

Edit `frontend/.env.local`:

```bash
# frontend/.env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_SECRET=your-random-secret-key-here
BETTER_AUTH_URL=http://localhost:3000
NODE_ENV=development
```

**Important**: The `NEXT_PUBLIC_API_URL` must match the backend URL in Docker Compose.

---

### Step 4: Install Dependencies (Without Docker)

If you prefer to run services locally without Docker:

#### Backend Dependencies

```bash
cd backend

# Create virtual environment with uv
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -r requirements.txt
```

#### Frontend Dependencies

```bash
cd frontend

# Install Node.js dependencies
npm install
```

---

### Step 5: Run Database Migrations

The database schema must be created before starting the application.

#### Option A: Using Docker Compose (Recommended)

Migrations will run automatically when the backend container starts (configured in `docker-compose.yml`).

#### Option B: Running Manually (Local Development)

```bash
cd backend
source .venv/bin/activate

# Run migrations
alembic upgrade head

# Verify migrations
alembic current
```

Expected output:
```
INFO  [alembic.runtime.migration] Running upgrade  -> 001_initial_schema, Initial schema: users and tasks tables
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
001_initial_schema (head)
```

---

### Step 6: Start the Application

#### Option A: Using Docker Compose (Recommended)

From the project root:

```bash
docker-compose up
```

**First run** will take 3-5 minutes to build images. Subsequent runs are instant.

Watch for these log messages indicating services are ready:
```
backend_1   | INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
frontend_1  | ✓ Ready in 2.3s
frontend_1  | - Local:   http://localhost:3000
```

#### Option B: Running Locally (Without Docker)

**Terminal 1 - Backend**:
```bash
cd backend
source .venv/bin/activate
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Frontend**:
```bash
cd frontend
npm run dev
```

---

### Step 7: Verify Installation

#### 1. Health Check - Backend

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-12-19T12:34:56.789Z",
  "version": "1.0.0",
  "checks": {
    "database": {
      "status": "connected",
      "latency_ms": 12
    },
    "api": {
      "status": "operational",
      "uptime_seconds": 3600
    }
  }
}
```

#### 2. API Documentation

Open in browser: http://localhost:8000/docs

You should see the FastAPI Swagger UI with documented endpoints.

#### 3. Frontend Application

Open in browser: http://localhost:3000

You should see the "Hello World" page.

#### 4. Database Connection

Check that tables were created:

```bash
# Using psql (if installed)
psql $DATABASE_URL -c "\dt"

# Expected output:
#          List of relations
#  Schema |   Name   | Type  |  Owner
# --------+----------+-------+---------
#  public | tasks    | table | user
#  public | users    | table | user
```

---

## Common Commands

### Docker Compose

```bash
# Start services in foreground (see logs)
docker-compose up

# Start services in background (detached mode)
docker-compose up -d

# Stop services
docker-compose down

# Rebuild images (after dependency changes)
docker-compose up --build

# View logs
docker-compose logs -f              # All services
docker-compose logs -f backend      # Backend only
docker-compose logs -f frontend     # Frontend only

# Execute command in running container
docker-compose exec backend bash
docker-compose exec frontend sh

# Restart a single service
docker-compose restart backend
```

### Backend (Local Development)

```bash
cd backend
source .venv/bin/activate

# Run development server with hot reload
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

# Run tests
pytest

# Run tests with coverage
pytest --cov=src --cov-report=html

# Lint code
ruff check src tests

# Format code
black src tests

# Type check
mypy src

# Run all quality checks
ruff check src && black --check src && mypy src && pytest
```

### Frontend (Local Development)

```bash
cd frontend

# Run development server
npm run dev

# Build for production
npm run build

# Start production server (after build)
npm start

# Run tests
npm test

# Run tests with coverage
npm run test:cov

# Lint code
npm run lint

# Format code
npm run format

# Type check
npm run type-check

# Run all quality checks
npm run check
```

### Database Migrations

```bash
cd backend
source .venv/bin/activate

# Create a new migration (auto-generate from model changes)
alembic revision --autogenerate -m "Add new field to tasks"

# Apply migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1

# Show current migration version
alembic current

# Show migration history
alembic history

# Rollback to specific migration
alembic downgrade <revision_id>
```

---

## Troubleshooting

### Issue: Docker Compose fails to start

**Symptom**: `Error: Cannot start service backend: driver failed`

**Solutions**:
1. Check Docker is running: `docker ps`
2. Ensure ports 3000 and 8000 are not in use:
   ```bash
   # On macOS/Linux
   lsof -i :3000
   lsof -i :8000

   # On Windows
   netstat -ano | findstr :3000
   netstat -ano | findstr :8000
   ```
3. Stop conflicting services or change ports in `docker-compose.yml`

---

### Issue: Database connection fails

**Symptom**: `OperationalError: could not connect to server`

**Solutions**:
1. Verify `DATABASE_URL` in `backend/.env`:
   ```bash
   echo $DATABASE_URL
   ```
2. Test connection manually:
   ```bash
   psql $DATABASE_URL -c "SELECT 1"
   ```
3. Check Neon dashboard to ensure database is active (not sleeping)
4. Verify `sslmode=require` is in connection string
5. Check firewall/network allows connections to Neon (port 5432)

---

### Issue: Migrations fail with "relation already exists"

**Symptom**: `sqlalchemy.exc.ProgrammingError: (psycopg2.errors.DuplicateTable) relation "users" already exists`

**Solutions**:
1. Check current migration version:
   ```bash
   alembic current
   ```
2. If migrations are out of sync, mark current state without running migrations:
   ```bash
   alembic stamp head
   ```
3. If database is corrupted, drop and recreate:
   ```bash
   # WARNING: This deletes all data!
   alembic downgrade base
   alembic upgrade head
   ```

---

### Issue: Frontend shows "Failed to fetch" error

**Symptom**: Network error when calling API from frontend

**Solutions**:
1. Verify backend is running: `curl http://localhost:8000/health`
2. Check `NEXT_PUBLIC_API_URL` in `frontend/.env.local`
3. Check browser console for CORS errors
4. Verify `CORS_ORIGINS` includes `http://localhost:3000` in `backend/.env`
5. Clear browser cache and hard refresh (Ctrl+Shift+R)

---

### Issue: Hot reload not working

**Symptom**: Code changes don't trigger automatic reload

**Solutions (Backend)**:
1. Ensure `--reload` flag is used: `uvicorn src.main:app --reload`
2. Check volume mounts in `docker-compose.yml`:
   ```yaml
   volumes:
     - ./backend:/app
   ```
3. On Windows, ensure WSL2 file system is used (not /mnt/c/)

**Solutions (Frontend)**:
1. Delete `.next` directory and restart:
   ```bash
   rm -rf .next
   npm run dev
   ```
2. Check volume mounts exclude `.next`:
   ```yaml
   volumes:
     - ./frontend:/app
     - /app/.next
     - /app/node_modules
   ```

---

### Issue: Node.js version mismatch

**Symptom**: `error engine-strict: The module does not satisfy the required Node.js version`

**Solutions**:
1. Check Node.js version: `node --version`
2. Install correct version using nvm:
   ```bash
   # Install nvm (if not installed): https://github.com/nvm-sh/nvm
   nvm install 22
   nvm use 22
   ```
3. Alternatively, update `package.json` to accept your Node version

---

### Issue: Port already in use

**Symptom**: `Error: listen EADDRINUSE: address already in use :::3000`

**Solutions**:
1. Find process using the port:
   ```bash
   # On macOS/Linux
   lsof -ti:3000

   # On Windows
   netstat -ano | findstr :3000
   ```
2. Kill the process:
   ```bash
   # On macOS/Linux
   kill -9 $(lsof -ti:3000)

   # On Windows
   taskkill /PID <PID> /F
   ```
3. Or change the port in `docker-compose.yml` and `.env.local`

---

### Issue: Python virtual environment activation fails

**Symptom**: `bash: .venv/bin/activate: No such file or directory`

**Solutions**:
1. Ensure you're in the `backend/` directory:
   ```bash
   pwd  # Should show: /path/to/hackathon-2-todo-phase-2/backend
   ```
2. Create virtual environment:
   ```bash
   uv venv
   ```
3. On Windows, use: `.venv\Scripts\activate`

---

### Issue: Docker Compose build is slow

**Symptom**: `docker-compose up --build` takes 5+ minutes

**Solutions**:
1. Use Docker BuildKit for faster builds:
   ```bash
   export DOCKER_BUILDKIT=1
   export COMPOSE_DOCKER_CLI_BUILD=1
   docker-compose up --build
   ```
2. Cache dependencies by separating install step in Dockerfile
3. Increase Docker memory allocation (Docker Desktop → Settings → Resources)

---

### Issue: "Module not found" error in frontend

**Symptom**: `Module not found: Can't resolve '@/components/ui/button'`

**Solutions**:
1. Verify import alias in `tsconfig.json`:
   ```json
   {
     "compilerOptions": {
       "paths": {
         "@/*": ["./*"]
       }
     }
   }
   ```
2. Restart TypeScript server in VSCode: `Ctrl+Shift+P` → "Restart TypeScript Server"
3. Delete `node_modules` and reinstall:
   ```bash
   rm -rf node_modules package-lock.json
   npm install
   ```

---

## Next Steps

After successful setup:

1. **Explore the API**:
   - Open http://localhost:8000/docs
   - Try the health check endpoint
   - Review the auto-generated OpenAPI schema

2. **Inspect the Database**:
   - Connect using your database client
   - Review the `users` and `tasks` table schemas
   - Insert sample data for testing

3. **Run the Test Suite**:
   ```bash
   # Backend tests
   cd backend && pytest

   # Frontend tests
   cd frontend && npm test
   ```

4. **Read the Documentation**:
   - `/specs/002-project-setup/plan.md` - Implementation plan
   - `/specs/002-project-setup/data-model.md` - Database schema
   - `/specs/002-project-setup/contracts/` - API contracts

5. **Start Development**:
   - Proceed to Feature 3: Authentication
   - Or explore the codebase to understand the architecture

---

## Development Workflow

### Making Changes

1. **Create a feature branch**:
   ```bash
   git checkout -b 003-authentication
   ```

2. **Make changes** with hot reload enabled (changes reflect immediately)

3. **Run tests** to ensure nothing breaks:
   ```bash
   cd backend && pytest
   cd frontend && npm test
   ```

4. **Run linters and formatters**:
   ```bash
   cd backend && ruff check --fix src && black src
   cd frontend && npm run lint --fix && npm run format
   ```

5. **Commit changes** following Conventional Commits:
   ```bash
   git add .
   git commit -m "feat: add user authentication endpoint"
   ```

6. **Push and create PR**:
   ```bash
   git push origin 003-authentication
   # Create PR on GitHub/GitLab
   ```

---

## Getting Help

### Resources

- **Project Documentation**: `/specs/002-project-setup/`
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Next.js Docs**: https://nextjs.org/docs
- **Neon Docs**: https://neon.tech/docs
- **Shadcn/ui Docs**: https://ui.shadcn.com/

### Support Channels

- **GitHub Issues**: Report bugs or request features
- **Team Chat**: [Insert team communication channel]
- **Stack Overflow**: Tag questions with `fastapi`, `nextjs`, `postgresql`

---

## Summary

You should now have:

- ✅ Docker Compose running both frontend and backend
- ✅ Database migrations applied to Neon PostgreSQL
- ✅ Health check endpoint responding at http://localhost:8000/health
- ✅ Frontend application accessible at http://localhost:3000
- ✅ API documentation at http://localhost:8000/docs
- ✅ Hot reload working for both services

**Estimated Setup Time**: 5-10 minutes (excluding Docker image download time)

If you encountered any issues not covered in this guide, please update this document or reach out to the team.

Happy coding! 🚀
