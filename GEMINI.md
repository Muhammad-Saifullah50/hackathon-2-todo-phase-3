# Gemini CLI Rules - Todo Application (Phase 2)

This file contains project-specific guidelines for Gemini CLI when working on this full-stack Todo application.

## Project Overview

**Todo Application (Phase 2)** - A modern, full-stack task management system with a FastAPI backend and a Next.js frontend.

**Architecture:**
- **Backend:** FastAPI, SQLModel (SQLAlchemy + Pydantic), Alembic migrations, PostgreSQL.
- **Frontend:** Next.js 15 (App Router), React 19, TanStack Query, Tailwind CSS 4.
- **DevOps:** Docker Compose for local development.

## Core Guarantees & Workflows

### 1. Spec-Driven Development (SDD)
- Always refer to `specs/` for feature requirements.
- Maintain `history/prompts/` for all significant interactions.
- Suggest ADRs for architectural changes: `/sp.adr <title>`.

### 2. Information Gathering
- Use `codebase_investigator` for complex analysis.
- Use `run_shell_command` to verify state (e.g., `docker ps`, `npm list`, `pip list`).

## Development Guidelines

### Root Level
- **Docker:** Use `docker-compose.yml` for orchestration.
- **Tasks:** Check `tasks.json` for project-level tasks.
- **Specs:** All new features must have a spec in `specs/`.

### Quality Standards
- **Linting:** Ensure `ruff` (backend) and `eslint` (frontend) pass.
- **Testing:** Always run `pytest` (backend) and `npm test` (frontend) before finalizing.
- **Types:** Strictly adhere to TypeScript (frontend) and Python type hints (backend).

## Project Structure

- `backend/`: Python FastAPI service.
- `frontend/`: Next.js frontend application.
- `specs/`: Feature specifications and plans.
- `history/`: Prompt history and ADRs.
- `docker-compose.yml`: Local development environment.

## Success Criteria
- Code is clean, documented, and tested.
- Changes are minimal and purposeful.
- PHRs are created for every prompt.