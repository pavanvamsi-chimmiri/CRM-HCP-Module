# Architecture

> Documentation for the AI CRM platform architecture. Application code is not yet implemented.

## Overview

AI CRM is a full-stack enterprise application with a clear separation between presentation, business logic, data access, and AI orchestration layers.

## Frontend Architecture

- **Feature modules** (`src/features/`) — Self-contained domains (auth, contacts, deals, AI assistant)
- **Shared components** (`src/components/`) — Reusable UI across features
- **Redux Toolkit** (`src/store/`) — Global state with feature slices
- **Service layer** (`src/services/`) — Axios-based API clients
- **Route-based pages** (`src/pages/` + `src/routes/`)

## Backend Architecture

```
Request → Middleware → API Endpoints → Services → Repositories → Database
                                              ↓
                                         AI Agents (LangGraph)
                                              ↓
                                          Groq API
```

| Layer | Responsibility |
|-------|----------------|
| `api/v1/endpoints` | HTTP routing, request validation |
| `schemas` | Pydantic models for I/O |
| `services` | Business rules and orchestration |
| `repositories` | Database queries (CRUD) |
| `models` | SQLAlchemy ORM entities |
| `ai/` | LangGraph workflows, agents, tools |

## AI Subsystem

The `backend/app/ai/` module will contain:

- **graphs/** — LangGraph state machine definitions
- **agents/** — CRM-specific agent implementations
- **prompts/** — System and task prompt templates
- **tools/** — Callable tools (e.g., search contacts, update deals)

## Database

PostgreSQL with async SQLAlchemy (`asyncpg`) for runtime and sync driver (`psycopg2`) for Alembic migrations.

## Deployment

- **Development** — Docker Compose with hot-reload
- **Production** — Separate container images for frontend (nginx) and backend (gunicorn + uvicorn workers)
