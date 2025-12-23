# Research: Project Setup & Architecture

**Feature**: Project Setup & Architecture
**Branch**: `002-project-setup`
**Research Date**: 2025-12-19

## Overview

This document captures research findings for setting up a full-stack web application with Next.js 16 frontend, FastAPI backend, and Docker Compose orchestration with Neon PostgreSQL.

---

## 1. Docker Compose Best Practices for Next.js + FastAPI

### Multi-Service Architecture

**Key Principles**:
- Use separate services for frontend, backend, and database
- Implement health checks for service readiness
- Use dependency ordering (`depends_on` with `condition: service_healthy`)
- Mount volumes for hot reload during development
- Use environment-specific compose files (docker-compose.yml for dev, docker-compose.prod.yml for production)

**Docker Compose Structure**:
```yaml
version: '3.9'

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
      - /app/node_modules
      - /app/.next
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
      - NODE_ENV=development
    depends_on:
      backend:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/api/health"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.dev
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - CORS_ORIGINS=http://localhost:3000
      - LOG_LEVEL=DEBUG
    env_file:
      - ./backend/.env
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 40s
```

**Best Practices**:
1. **Health Checks**: Implement `/health` endpoints in both services
2. **Volume Mounts**: Use named volumes for node_modules and .next to avoid overwriting
3. **Port Mapping**: Expose consistent ports (3000 for frontend, 8000 for backend)
4. **Environment Variables**: Use `.env` files excluded from git, provide `.env.example` templates
5. **Development vs Production**: Use multi-stage Dockerfiles (dev with hot reload, prod optimized)

**Hot Reload Configuration**:
- Frontend: Next.js dev server watches file changes automatically with volume mounts
- Backend: Use `uvicorn --reload` flag in dev Dockerfile CMD

---

## 2. Next.js 16 Project Initialization

**Note**: As of December 2025, Next.js 15 is the latest stable version. Using Next.js 15 with React 19 for this research.

### Installation Command

```bash
npx create-next-app@latest frontend --typescript --tailwind --app --no-src-dir --import-alias "@/*"
```

**Flags Explained**:
- `--typescript`: Enable TypeScript
- `--tailwind`: Include Tailwind CSS configuration
- `--app`: Use App Router (recommended over Pages Router)
- `--no-src-dir`: Place code in root `app/` directory (not `src/`)
- `--import-alias "@/*"`: Enable absolute imports with `@/` prefix

### Project Structure (App Router)

```
frontend/
├── app/
│   ├── layout.tsx           # Root layout (wraps all pages)
│   ├── page.tsx             # Home page (/)
│   ├── api/
│   │   └── health/
│   │       └── route.ts     # API route for health check
│   ├── (auth)/              # Route group (doesn't affect URL)
│   │   ├── login/
│   │   │   └── page.tsx
│   │   └── signup/
│   │       └── page.tsx
│   └── dashboard/
│       ├── layout.tsx       # Nested layout for dashboard
│       └── page.tsx
├── components/
│   ├── ui/                  # Shadcn/ui components
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   └── ...
│   └── features/            # Feature-specific components
│       └── task-list.tsx
├── lib/
│   ├── api.ts               # API client utilities
│   ├── utils.ts             # Utility functions
│   └── validations.ts       # Zod schemas
├── public/                  # Static assets
├── styles/
│   └── globals.css          # Global styles + Tailwind imports
├── .env.local               # Local environment variables (gitignored)
├── .env.example             # Template for environment variables
├── next.config.ts           # Next.js configuration
├── tailwind.config.ts       # Tailwind configuration
├── tsconfig.json            # TypeScript configuration
└── package.json
```

### Key Configuration Files

**next.config.ts**:
```typescript
import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  reactStrictMode: true,
  experimental: {
    serverActions: {
      bodySizeLimit: '2mb',
    },
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
  },
};

export default nextConfig;
```

**tailwind.config.ts** (with Shadcn/ui):
```typescript
import type { Config } from 'tailwindcss';

const config: Config = {
  darkMode: ['class'],
  content: [
    './pages/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './app/**/*.{ts,tsx}',
    './src/**/*.{ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        primary: {
          DEFAULT: 'hsl(var(--primary))',
          foreground: 'hsl(var(--primary-foreground))',
        },
        // ... other Shadcn color tokens
      },
      borderRadius: {
        lg: 'var(--radius)',
        md: 'calc(var(--radius) - 2px)',
        sm: 'calc(var(--radius) - 4px)',
      },
    },
  },
  plugins: [require('tailwindcss-animate')],
};

export default config;
```

**Installing Shadcn/ui**:
```bash
npx shadcn@latest init
# Follow prompts to configure base styles
npx shadcn@latest add button card input label toast
```

### API Client Setup (TanStack Query)

```bash
npm install @tanstack/react-query axios zod
```

**lib/api.ts**:
```typescript
import axios from 'axios';

export const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Enable cookies for session-based auth
});

// Add request/response interceptors for auth token handling
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

**app/providers.tsx** (TanStack Query setup):
```typescript
'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useState } from 'react';

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(() => new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 60 * 1000, // 1 minute
        refetchOnWindowFocus: false,
      },
    },
  }));

  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
}
```

---

## 3. FastAPI Project Structure with SQLModel

### Installation

```bash
mkdir backend && cd backend
uv venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
uv pip install fastapi uvicorn[standard] sqlmodel alembic asyncpg python-dotenv pydantic-settings
uv pip install --dev pytest pytest-asyncio httpx pytest-cov ruff black mypy
```

### Project Structure

```
backend/
├── alembic/                 # Alembic migration files
│   ├── versions/
│   │   └── 001_initial_schema.py
│   ├── env.py              # Alembic environment config
│   └── script.py.mako      # Migration template
├── src/
│   ├── __init__.py
│   ├── main.py             # FastAPI app entry point
│   ├── config.py           # Settings management
│   ├── database.py         # Database connection & session
│   ├── models/             # SQLModel database models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── task.py
│   ├── schemas/            # Pydantic request/response schemas
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── task.py
│   │   └── responses.py    # Standardized response formats
│   ├── api/                # API routes
│   │   ├── __init__.py
│   │   ├── health.py
│   │   ├── users.py
│   │   └── tasks.py
│   ├── services/           # Business logic layer
│   │   ├── __init__.py
│   │   ├── user_service.py
│   │   └── task_service.py
│   └── validators/         # Input validation
│       ├── __init__.py
│       └── task_validators.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py         # Pytest fixtures
│   ├── unit/
│   │   ├── test_services.py
│   │   └── test_validators.py
│   └── integration/
│       └── test_api.py
├── .env                    # Local environment (gitignored)
├── .env.example            # Template
├── alembic.ini             # Alembic configuration
├── pyproject.toml          # Project metadata + tool configs
└── requirements.txt        # Dependencies
```

### Key Implementation Files

**src/config.py** (using pydantic-settings):
```python
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    # Database
    database_url: str

    # CORS
    cors_origins: list[str] = ["http://localhost:3000"]

    # Security
    secret_key: str = "dev-secret-key-change-in-production"

    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    # Environment
    environment: Literal["development", "staging", "production"] = "development"

settings = Settings()
```

**src/database.py** (async SQLModel with PostgreSQL):
```python
from sqlmodel import SQLModel, create_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from .config import settings

# Convert postgresql:// to postgresql+asyncpg:// for async
DATABASE_URL = settings.database_url.replace(
    "postgresql://", "postgresql+asyncpg://"
)

engine = create_async_engine(
    DATABASE_URL,
    echo=settings.log_level == "DEBUG",
    future=True,
)

async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_session() -> AsyncSession:
    async with async_session_maker() as session:
        yield session

async def init_db():
    """Create database tables (development only, use Alembic in production)"""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
```

**src/main.py**:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .config import settings
from .api import health, tasks, users

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize database connection
    # await init_db()  # Only in dev, use Alembic migrations in production
    yield
    # Shutdown: Close connections
    pass

app = FastAPI(
    title="Todo API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(tasks.router, prefix="/api/v1/tasks", tags=["tasks"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
```

### SQLModel vs SQLAlchemy

**SQLModel** (recommended for this project):
- Built on top of SQLAlchemy and Pydantic
- Single model class for database and API schemas
- Native async support with SQLAlchemy 2.0
- Better type hints and IDE support
- Simpler for CRUD operations

**Example SQLModel**:
```python
from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4
from datetime import datetime

class TaskBase(SQLModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    status: str = Field(default="pending")

class Task(TaskBase, table=True):
    """Database model"""
    __tablename__ = "tasks"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class TaskCreate(TaskBase):
    """Request schema for creating task"""
    pass

class TaskResponse(TaskBase):
    """Response schema"""
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
```

---

## 4. Alembic Setup for Database Migrations

### Initialization

```bash
cd backend
alembic init alembic
```

### Configuration

**alembic.ini**:
```ini
[alembic]
script_location = alembic
prepend_sys_path = .
version_path_separator = os

# Use env var for database URL (don't hardcode)
sqlalchemy.url =

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

**alembic/env.py** (async-compatible):
```python
import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context
from src.config import settings
from src.models import *  # Import all models
from sqlmodel import SQLModel

# Alembic Config object
config = context.config

# Set database URL from environment
config.set_main_option("sqlalchemy.url", settings.database_url)

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Target metadata for autogenerate
target_metadata = SQLModel.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations() -> None:
    """Run migrations in 'online' mode with async engine."""
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = settings.database_url.replace(
        "postgresql://", "postgresql+asyncpg://"
    )

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

### Creating Migrations

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "Initial schema: users and tasks"

# Review the generated migration in alembic/versions/

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Show current migration version
alembic current

# Show migration history
alembic history
```

### Migration Best Practices

1. **Review autogenerated migrations**: Alembic may miss some changes (indexes, constraints)
2. **Write reversible migrations**: Always implement `downgrade()` function
3. **Test migrations on staging**: Never run untested migrations in production
4. **Version control migrations**: Commit migration files to git
5. **One logical change per migration**: Keep migrations focused
6. **Add data migrations separately**: Don't mix schema changes with data changes

---

## 5. Neon PostgreSQL Connection Patterns

### What is Neon?

Neon is a serverless PostgreSQL platform with:
- Automatic scaling (scale to zero when idle)
- Branching (create database branches like git)
- Instant provisioning (no waiting for database setup)
- Built-in connection pooling
- Pay-per-use pricing

### Connection String Format

```
postgresql://[user]:[password]@[host]/[database]?sslmode=require
```

**Example**:
```
postgresql://user:pass@ep-cool-name-123456.us-east-2.aws.neon.tech/neondb?sslmode=require
```

### Environment Configuration

**.env.example**:
```bash
# Neon PostgreSQL
DATABASE_URL=postgresql://user:password@host.neon.tech/dbname?sslmode=require

# Backend Configuration
SECRET_KEY=your-secret-key-here
CORS_ORIGINS=["http://localhost:3000"]
LOG_LEVEL=INFO
```

**.env** (actual values, gitignored):
```bash
DATABASE_URL=postgresql://actual_user:actual_pass@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require
SECRET_KEY=actual-secret-key-from-random-generator
CORS_ORIGINS=["http://localhost:3000"]
LOG_LEVEL=DEBUG
```

### Connection Pooling with SQLAlchemy

```python
from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_size=10,              # Number of connections to maintain
    max_overflow=20,           # Additional connections when pool exhausted
    pool_timeout=30,           # Seconds to wait for connection
    pool_recycle=3600,         # Recycle connections after 1 hour
    pool_pre_ping=True,        # Test connections before using
)
```

### Neon-Specific Optimizations

**Connection String Options**:
```
postgresql://...?sslmode=require&connect_timeout=10&application_name=todo-api
```

- `sslmode=require`: Enforce SSL (mandatory for Neon)
- `connect_timeout=10`: Connection timeout in seconds
- `application_name=todo-api`: Identify connections in Neon dashboard

**Using Neon Branching for Testing**:
```bash
# Create a branch for testing migrations
neon branches create --project-id xxx --parent main testing

# Get branch connection string
neon connection-string testing

# Run tests against branch
DATABASE_URL=<branch-url> pytest tests/
```

### Error Handling

```python
from sqlalchemy.exc import OperationalError, TimeoutError
from fastapi import HTTPException

async def get_tasks():
    try:
        async with async_session_maker() as session:
            result = await session.execute(select(Task))
            return result.scalars().all()
    except OperationalError as e:
        # Database connection failed
        logger.error(f"Database connection error: {e}")
        raise HTTPException(
            status_code=503,
            detail="Database unavailable. Please try again later."
        )
    except TimeoutError as e:
        # Query took too long
        logger.error(f"Database timeout: {e}")
        raise HTTPException(
            status_code=504,
            detail="Database query timeout. Please try again."
        )
```

---

## 6. Testing Setup

### Backend Testing (pytest + httpx)

**Installation**:
```bash
uv pip install --dev pytest pytest-asyncio pytest-cov httpx
```

**tests/conftest.py** (shared fixtures):
```python
import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from sqlmodel import SQLModel, create_engine
from sqlmodel.pool import StaticPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from src.main import app
from src.database import get_session

# Use in-memory SQLite for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
async def test_engine():
    """Create test database engine"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
    await engine.dispose()

@pytest.fixture(scope="function")
async def test_session(test_engine):
    """Create test database session"""
    async_session_maker = async_sessionmaker(
        test_engine, expire_on_commit=False
    )
    async with async_session_maker() as session:
        yield session

@pytest.fixture(scope="function")
async def client(test_session):
    """Create test HTTP client"""
    async def override_get_session():
        yield test_session

    app.dependency_overrides[get_session] = override_get_session

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
```

**tests/integration/test_health.py**:
```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "database" in data
```

### Frontend Testing (Vitest + React Testing Library)

**Installation**:
```bash
npm install --save-dev vitest @testing-library/react @testing-library/jest-dom @testing-library/user-event jsdom
```

**vitest.config.ts**:
```typescript
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./tests/setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'tests/',
        '*.config.ts',
      ],
    },
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './'),
    },
  },
});
```

**tests/setup.ts**:
```typescript
import '@testing-library/jest-dom';
import { cleanup } from '@testing-library/react';
import { afterEach } from 'vitest';

// Cleanup after each test
afterEach(() => {
  cleanup();
});
```

**Example Component Test**:
```typescript
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Button } from '@/components/ui/button';

describe('Button', () => {
  it('renders button with text', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByRole('button')).toHaveTextContent('Click me');
  });

  it('applies variant styles', () => {
    render(<Button variant="destructive">Delete</Button>);
    const button = screen.getByRole('button');
    expect(button).toHaveClass('bg-destructive');
  });
});
```

---

## 7. Code Quality Tools Configuration

### Backend (Python)

**pyproject.toml**:
```toml
[project]
name = "todo-api"
version = "1.0.0"
requires-python = ">=3.13"

[tool.black]
line-length = 100
target-version = ['py313']
include = '\.pyi?$'

[tool.ruff]
line-length = 100
target-version = "py313"
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "UP",  # pyupgrade
]
ignore = ["E501"]  # Line too long (handled by black)

[tool.mypy]
python_version = "3.13"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
asyncio_mode = "auto"
```

**package.json scripts** (for convenience):
```json
{
  "scripts": {
    "format": "black src tests",
    "format:check": "black --check src tests",
    "lint": "ruff check src tests",
    "lint:fix": "ruff check --fix src tests",
    "type-check": "mypy src",
    "test": "pytest",
    "test:cov": "pytest --cov=src --cov-report=html",
    "check": "npm run format:check && npm run lint && npm run type-check && npm run test"
  }
}
```

### Frontend (TypeScript)

**.eslintrc.json**:
```json
{
  "extends": [
    "next/core-web-vitals",
    "plugin:@typescript-eslint/recommended"
  ],
  "rules": {
    "@typescript-eslint/no-unused-vars": "error",
    "@typescript-eslint/no-explicit-any": "error",
    "react-hooks/rules-of-hooks": "error",
    "react-hooks/exhaustive-deps": "warn"
  }
}
```

**.prettierrc**:
```json
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 100,
  "tabWidth": 2,
  "useTabs": false
}
```

**package.json scripts**:
```json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "format": "prettier --write .",
    "format:check": "prettier --check .",
    "type-check": "tsc --noEmit",
    "test": "vitest run",
    "test:watch": "vitest",
    "test:cov": "vitest run --coverage",
    "check": "npm run format:check && npm run lint && npm run type-check && npm run test"
  }
}
```

---

## 8. Docker Multi-Stage Builds

### Frontend Dockerfile

**Dockerfile.dev** (development with hot reload):
```dockerfile
FROM node:22-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]
```

**Dockerfile** (production optimized):
```dockerfile
# Stage 1: Dependencies
FROM node:22-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

# Stage 2: Build
FROM node:22-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 3: Production
FROM node:22-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["node", "server.js"]
```

### Backend Dockerfile

**Dockerfile.dev**:
```dockerfile
FROM python:3.13-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN uv pip install --system -r requirements.txt

# Copy source code
COPY . .

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

**Dockerfile** (production):
```dockerfile
FROM python:3.13-slim AS builder

WORKDIR /app

RUN pip install uv

COPY requirements.txt .
RUN uv pip install --system --no-cache-dir -r requirements.txt

FROM python:3.13-slim

WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

RUN adduser --disabled-password --gecos '' apiuser
USER apiuser

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

---

## Summary

This research covers the foundational technologies for the Project Setup & Architecture feature:

1. **Docker Compose**: Multi-service orchestration with health checks and hot reload
2. **Next.js 16**: App Router, TypeScript, Shadcn/ui, TanStack Query setup
3. **FastAPI**: Async SQLModel, layered architecture (API → Services → Database)
4. **Alembic**: Async-compatible migrations for schema versioning
5. **Neon PostgreSQL**: Serverless PostgreSQL with connection pooling
6. **Testing**: pytest (backend), Vitest + RTL (frontend) with fixtures
7. **Code Quality**: Black, Ruff, mypy (backend), ESLint, Prettier, TSC (frontend)
8. **Docker**: Multi-stage builds for development and production

**Next Steps**:
- Define database schema in `data-model.md`
- Document API contracts in `contracts/`
- Create quickstart guide in `quickstart.md`
- Fill out `plan.md` template with architecture decisions
