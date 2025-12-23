---
id: 0001
title: Setup Gemini CLI Rules
stage: general
date: 2025-12-19
surface: agent
model: Gemini 2.0 Flash
feature: none
branch: 002-project-setup
user: Saifullah
command: none
labels: [setup, documentation, configuration]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - GEMINI.md
 - frontend/GEMINI.md
 - backend/GEMINI.md
tests:
 - n/a
---

## Prompt

create a gemini.md file tailored to the projhect at the root level, in the frontend and in the backend fiolder

## Response snapshot

I have created the requested GEMINI.md files at the root, in the frontend/ folder, and in the backend/ folder, each tailored to the specific technologies and standards used in those parts of the project.

## Outcome

- ✅ Impact: Established clear, project-specific guidelines for the Gemini CLI agent across the entire codebase.
- 🧪 Tests: n/a
- 📁 Files: Created/updated GEMINI.md in root, frontend, and backend.
- 🔁 Next prompts: Continue with project setup or feature implementation.
- 🧠 Reflection: Leveraging existing CLAUDE.md and project configuration files (package.json, pyproject.toml) allowed for highly tailored and accurate agent instructions.

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): PASS
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): null
