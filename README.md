# HCP CRM — AI-Powered Healthcare Professional Management

Enterprise-grade CRM for pharmaceutical and medical sales teams. Log HCP interactions, track follow-ups, and leverage AI to extract structured data from natural language and voice notes.

Built with **React**, **FastAPI**, **PostgreSQL**, **LangGraph**, and **Groq**.

<p align="center">
  <img src="https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=white" alt="React 18" />
  <img src="https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white" alt="PostgreSQL 16" />
  <img src="https://img.shields.io/badge/LangGraph-AI%20Agents-FF6B6B" alt="LangGraph" />
  <img src="https://img.shields.io/badge/Groq-LLM%20%2B%20Whisper-F55036" alt="Groq" />
  <img src="https://img.shields.io/badge/TypeScript-5.7-3178C6?logo=typescript&logoColor=white" alt="TypeScript" />
</p>

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Folder Structure](#folder-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Environment Variables](#environment-variables)
- [Running the Frontend](#running-the-frontend)
- [Running the Backend](#running-the-backend)
- [Docker](#docker)
- [LangGraph](#langgraph)
- [Groq](#groq)
- [PostgreSQL](#postgresql)
- [Screenshots](#screenshots)
- [Development](#development)
- [License](#license)

---

## Overview

HCP CRM helps field representatives manage Healthcare Professional (HCP) relationships efficiently:

| Feature | Description |
|---------|-------------|
| **Dashboard** | Interaction stats, recent visits, quick actions |
| **Log Interaction** | Structured form for visits, calls, and meetings |
| **AI Assistant** | Natural-language input with automatic form filling |
| **Voice Upload** | Audio → Groq Whisper transcription → summarize → extract |
| **History** | Search, filter, edit, and delete past interactions |
| **Settings** | Profile and application configuration |

### Tech Stack

| Layer | Technologies |
|-------|--------------|
| **Frontend** | React 18, Vite 6, TypeScript, Redux Toolkit, Tailwind CSS, React Router 7, React Hook Form, Zod, Axios |
| **Backend** | FastAPI, SQLAlchemy 2, Pydantic v2, Alembic, JWT auth |
| **Database** | PostgreSQL 16 |
| **AI** | LangGraph, Groq (`gemma2-9b-it`, `whisper-large-v3-turbo`) |
| **DevOps** | Docker Compose, GitHub Actions |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT (Browser)                               │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────┐  ┌──────────────────┐  │
│  │  Dashboard  │  │ Log Interact │  │  AI Assist  │  │  Voice Upload    │  │
│  └──────┬──────┘  └──────┬───────┘  └──────┬──────┘  └────────┬─────────┘  │
│         │                │                 │                   │            │
│         └────────────────┴─────────────────┴───────────────────┘            │
│                                    │                                        │
│                          Redux Toolkit + Axios                              │
└────────────────────────────────────┼────────────────────────────────────────┘
                                     │ HTTP/REST (JWT)
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           FASTAPI BACKEND                                   │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                  │
│  │  API Layer   │───►│   Services   │───►│     CRUD     │                  │
│  │  /api/v1/*   │    │  (business)  │    │   (data)     │                  │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘                  │
│         │                   │                   │                           │
│         │            ┌──────▼───────┐           │                           │
│         │            │  AI Subsystem │           │                           │
│         │            │  LangGraph    │           │                           │
│         │            └──────┬───────┘           │                           │
│         │                   │                   │                           │
└─────────┼───────────────────┼───────────────────┼───────────────────────────┘
          │                   │                   │
          │                   ▼                   ▼
          │            ┌─────────────┐    ┌─────────────┐
          │            │  Groq API   │    │ PostgreSQL  │
          │            │ LLM+Whisper │    │     16      │
          │            └─────────────┘    └─────────────┘
          │
          └── Auth (JWT) · CORS · Structured Logging
```

### Request Flow

1. **Frontend** sends authenticated requests via Axios interceptors.
2. **API endpoints** validate input with Pydantic schemas.
3. **Services** enforce business rules and orchestrate AI workflows.
4. **CRUD layer** persists data to PostgreSQL via async SQLAlchemy.
5. **LangGraph agents** handle intent detection, entity extraction, validation, and response generation.
6. **Groq** powers LLM inference (chat, summarize, extract) and Whisper speech-to-text.

### AI Pipelines

| Pipeline | Graph | Purpose |
|----------|-------|---------|
| **HCP Agent** | `graph.py` | Full interaction logging with save |
| **Form Assistant** | `graphs/assistant_graph.py` | Extract fields, ask follow-up questions |
| **Voice Upload** | Whisper → Summarize → Assistant | Transcribe audio and auto-fill form |

---

## Folder Structure

```
CRM-HCP-Module/
├── frontend/                          # React + Vite SPA
│   ├── public/                        # Static assets
│   ├── src/
│   │   ├── components/
│   │   │   ├── assistant/             # AI Assistant & Voice Upload panels
│   │   │   ├── layout/                # AppLayout, Sidebar
│   │   │   └── ui/                    # Button, Input, Card, Badge, etc.
│   │   ├── hooks/                     # Redux typed hooks
│   │   ├── pages/                     # Dashboard, LogInteraction, History, Settings
│   │   ├── routes/                    # React Router config & auth guards
│   │   ├── services/api/              # Axios API clients
│   │   ├── store/slices/              # Redux Toolkit slices
│   │   ├── types/                     # TypeScript interfaces
│   │   ├── utils/                     # Formatters, constants
│   │   ├── index.css                  # Tailwind + medical theme
│   │   └── main.tsx                   # App entry point
│   ├── Dockerfile
│   ├── package.json
│   └── vite.config.ts
│
├── backend/                           # FastAPI application
│   ├── app/
│   │   ├── api/
│   │   │   ├── deps.py                # Auth & DB dependencies
│   │   │   └── v1/
│   │   │       ├── endpoints/         # auth, users, interactions, assistant
│   │   │       └── router.py
│   │   ├── ai/
│   │   │   ├── agents/                # HCP agent, Form assistant agent
│   │   │   ├── graphs/                # LangGraph workflow definitions
│   │   │   ├── nodes/                 # Intent, extract, validate, respond
│   │   │   ├── prompts/               # LLM prompt templates
│   │   │   ├── tools/                 # 7 CRM tools (log, search, summarize…)
│   │   │   ├── groq_service.py        # Centralized Groq LLM service
│   │   │   ├── whisper_service.py     # Groq Whisper transcription
│   │   │   └── graph.py               # Main HCP agent graph
│   │   ├── core/                      # Config, security, logging
│   │   ├── crud/                      # Database access layer
│   │   ├── db/                        # Session, base models
│   │   ├── models/                    # HCP, Interaction, Followup, Material
│   │   ├── schemas/                   # Pydantic request/response models
│   │   ├── services/                  # Business logic
│   │   └── main.py                    # FastAPI app factory
│   ├── alembic/versions/              # Database migrations
│   ├── tests/                         # Unit & integration tests
│   ├── Dockerfile
│   └── requirements.txt
│
├── docs/
│   ├── ARCHITECTURE.md
│   └── screenshots/                   # Add UI screenshots here
│
├── scripts/
│   └── setup.sh                       # Local dev setup script
│
├── .github/workflows/                 # CI/CD pipelines
├── docker-compose.yml                 # Full-stack orchestration
├── Dockerfile                         # Root backend production image
├── .env.example                       # Environment template
├── package.json                       # Monorepo convenience scripts
└── README.md
```

---

## Prerequisites

| Requirement | Version |
|-------------|---------|
| Node.js | >= 20 |
| npm | >= 10 |
| Python | >= 3.11 |
| PostgreSQL | 16 (or Docker) |
| Docker & Docker Compose | Latest (recommended) |
| Groq API Key | [Get one free](https://console.groq.com/) |

---

## Installation

### Option A — Docker (recommended)

```bash
git clone https://github.com/pavanvamsi-chimmiri/CRM-HCP-Module.git
cd CRM-HCP-Module
cp .env.example .env
# Edit .env — set GROQ_API_KEY and secrets

docker compose up --build
```

### Option B — Local development

```bash
git clone https://github.com/pavanvamsi-chimmiri/CRM-HCP-Module.git
cd CRM-HCP-Module
cp .env.example .env

# Automated setup (venv, deps, migrations)
bash scripts/setup.sh

# Or manual setup:
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head

cd ../frontend
npm install
```

---

## Environment Variables

Copy `.env.example` to `.env` and configure:

### Application

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_NAME` | `AI CRM` | Application display name |
| `APP_ENV` | `development` | `development` or `production` |
| `APP_DEBUG` | `true` | Enable debug mode & API docs |
| `APP_SECRET_KEY` | — | Application secret (change in production) |

### Backend API

| Variable | Default | Description |
|----------|---------|-------------|
| `BACKEND_HOST` | `0.0.0.0` | Server bind host |
| `BACKEND_PORT` | `8000` | Server port |
| `API_V1_PREFIX` | `/api/v1` | API route prefix |
| `CORS_ORIGINS` | `http://localhost:5173` | Allowed frontend origins (comma-separated) |

### Frontend

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_BASE_URL` | `http://localhost:8000/api/v1` | Backend API URL |
| `VITE_APP_NAME` | `AI CRM` | Frontend app title |

### PostgreSQL

| Variable | Default | Description |
|----------|---------|-------------|
| `POSTGRES_USER` | `ai_crm` | Database user |
| `POSTGRES_PASSWORD` | `ai_crm_secret` | Database password |
| `POSTGRES_DB` | `ai_crm` | Database name |
| `POSTGRES_HOST` | `postgres` | Host (`localhost` for local dev) |
| `POSTGRES_PORT` | `5432` | Database port |
| `DATABASE_URL` | — | Async connection string (`postgresql+asyncpg://…`) |
| `DATABASE_URL_SYNC` | — | Sync connection string (Alembic migrations) |

### Authentication

| Variable | Default | Description |
|----------|---------|-------------|
| `JWT_SECRET_KEY` | — | JWT signing secret |
| `JWT_ALGORITHM` | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Access token lifetime |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Refresh token lifetime |

### Groq (AI)

| Variable | Default | Description |
|----------|---------|-------------|
| `GROQ_API_KEY` | — | **Required** for AI features |
| `GROQ_MODEL` | `gemma2-9b-it` | LLM model for chat, extract, summarize |
| `GROQ_WHISPER_MODEL` | `whisper-large-v3-turbo` | Speech-to-text model |
| `GROQ_MAX_TOKENS` | `4096` | Max response tokens |
| `GROQ_TEMPERATURE` | `0.7` | LLM temperature |

### LangGraph / AI Agent

| Variable | Default | Description |
|----------|---------|-------------|
| `AI_AGENT_ENABLED` | `true` | Enable/disable AI agents |
| `AI_MAX_CONVERSATION_HISTORY` | `20` | Max chat history messages |

### Logging

| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_LEVEL` | `INFO` | Log verbosity |
| `LOG_FORMAT` | `json` | `json` or `console` |

---

## Running the Frontend

### Development server

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173**

### Production build

```bash
cd frontend
npm run build      # TypeScript check + Vite build
npm run preview    # Preview production build locally
```

### Available scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start Vite dev server with HMR |
| `npm run build` | Production build to `dist/` |
| `npm run preview` | Serve production build |
| `npm run lint` | ESLint check |
| `npm run type-check` | TypeScript validation |
| `npm run format` | Prettier formatting |

### From monorepo root

```bash
npm run frontend:dev
npm run frontend:build
```

---

## Running the Backend

### Development server

```bash
cd backend
source .venv/bin/activate   # Windows: .venv\Scripts\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

| Endpoint | URL |
|----------|-----|
| API | http://localhost:8000/api/v1 |
| Swagger Docs | http://localhost:8000/docs |
| Health Check | http://localhost:8000/health |

### Database migrations

```bash
cd backend
source .venv/bin/activate
alembic upgrade head          # Apply all migrations
alembic revision --autogenerate -m "description"  # Create new migration
```

### Testing & linting

```bash
cd backend
pytest                        # Run test suite
pytest --cov=app              # With coverage
ruff check app tests          # Lint
```

### From monorepo root

```bash
npm run backend:dev
```

---

## Docker

### Development (full stack)

```bash
docker compose up --build
```

| Service | URL | Container |
|---------|-----|-----------|
| Frontend | http://localhost:5173 | `ai-crm-frontend` |
| Backend API | http://localhost:8000 | `ai-crm-backend` |
| API Docs | http://localhost:8000/docs | — |
| PostgreSQL | localhost:5432 | `ai-crm-postgres` |

### Useful commands

```bash
docker compose up -d          # Detached mode
docker compose down           # Stop all services
docker compose logs -f        # Stream logs
docker compose ps             # Service status
```

### Production images

```bash
# Backend
docker build -f Dockerfile --target production -t hcp-crm-backend .

# Frontend (nginx)
docker build -f frontend/Dockerfile --target production -t hcp-crm-frontend ./frontend
```

### Docker Compose services

```
postgres  →  PostgreSQL 16 with persistent volume
backend   →  FastAPI with hot-reload (dev target)
frontend  →  Vite dev server with API proxy (dev target)
```

---

## LangGraph

LangGraph orchestrates multi-step AI workflows as stateful graphs. Each node performs a discrete task and passes enriched state to the next node.

### HCP Agent Graph (`app/ai/graph.py`)

Full interaction logging pipeline:

```
START → Intent Detection → Entity Extraction → Validation
      → Recommendation → Save Interaction → Generate Response → END
```

### Form Assistant Graph (`app/ai/graphs/assistant_graph.py`)

Natural-language form filling (no auto-save):

```
START → Intent Detection → Entity Extraction → Prepare Context
      → Validation → Identify Missing Fields → Generate Response → END
```

### Agent Tools (`app/ai/tools/`)

| Tool | Description |
|------|-------------|
| `log_interaction` | Create a new HCP interaction record |
| `edit_interaction` | Update an existing interaction |
| `search_hcp` | Search healthcare professionals |
| `summarize_interaction` | Generate interaction summary |
| `recommend_followup` | Suggest follow-up actions |
| `sentiment` | Analyze interaction sentiment |
| `material_recommendation` | Recommend promotional materials |

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/assistant/parse` | Parse natural language → form fields |
| `POST` | `/api/v1/assistant/voice` | Upload audio → transcribe → extract → form fields |

---

## Groq

[Groq](https://groq.com/) provides fast LLM inference and speech-to-text via their LPU infrastructure.

### LLM (`gemma2-9b-it`)

Used for:

- Intent classification
- Entity extraction (doctor, topics, outcome, sentiment, follow-up)
- Interaction summarization
- Follow-up question generation
- Conversational assistant responses

Centralized in `backend/app/ai/groq_service.py`.

### Whisper (`whisper-large-v3-turbo`)

Used for voice note transcription in `backend/app/ai/whisper_service.py`.

**Supported formats:** MP3, WAV, M4A, WebM, OGG (max 25 MB)

**Voice upload pipeline:**

```
Audio File → Groq Whisper (transcribe) → Groq LLM (summarize)
           → LangGraph (extract fields) → Auto-fill form
```

### Getting a Groq API Key

1. Sign up at [console.groq.com](https://console.groq.com/)
2. Create an API key
3. Set `GROQ_API_KEY` in your `.env` file

---

## PostgreSQL

PostgreSQL 16 stores all application data with async SQLAlchemy (`asyncpg`) at runtime and sync driver (`psycopg2`) for Alembic migrations.

### Schema

| Table | Description |
|-------|-------------|
| `users` | Application users and authentication |
| `hcp` | Healthcare professional records |
| `interactions` | Visit/call logs with topics, sentiment, outcome |
| `materials` | Promotional materials catalog |
| `followups` | Scheduled follow-up actions |
| `interaction_materials` | Many-to-many link table |

### Migrations

| Revision | Description |
|----------|-------------|
| `001` | Initial schema (users) |
| `002` | HCP module schema |
| `003` | Extended interaction fields (attendees, materials, follow-up) |

### Local PostgreSQL (without Docker)

```bash
# Create database
createdb ai_crm

# Update .env
POSTGRES_HOST=localhost
DATABASE_URL=postgresql+asyncpg://ai_crm:ai_crm_secret@localhost:5432/ai_crm
DATABASE_URL_SYNC=postgresql://ai_crm:ai_crm_secret@localhost:5432/ai_crm

# Run migrations
cd backend && alembic upgrade head
```

---

## Screenshots

> Add screenshots to `docs/screenshots/` and reference them below.

### Dashboard

![Dashboard](docs/screenshots/dashboard.png)

*Overview of interaction stats, recent visits, and quick actions.*

### Log Interaction

![Log Interaction](docs/screenshots/log-interaction.png)

*Structured form with AI Assistant panel and voice upload.*

### AI Assistant

![AI Assistant](docs/screenshots/ai-assistant.png)

*Natural-language input with automatic field extraction.*

### Voice Upload

![Voice Upload](docs/screenshots/voice-upload.png)

*Audio upload with Groq Whisper transcription and form auto-fill.*

### Interaction History

![History](docs/screenshots/history.png)

*Searchable, filterable interaction history with edit and delete.*

### Login

![Login](docs/screenshots/login.png)

*Professional medical-themed authentication screen.*

---

## Development

### Monorepo scripts (from root)

```bash
npm run dev              # docker compose up
npm run dev:build        # docker compose up --build
npm run dev:down         # docker compose down
npm run frontend:dev     # Frontend only
npm run backend:dev      # Backend only
npm run setup            # Initial project setup
```

### API Overview

| Group | Prefix | Endpoints |
|-------|--------|-----------|
| Auth | `/api/v1/auth` | register, login, refresh, me |
| Users | `/api/v1/users` | CRUD |
| Interactions | `/api/v1/interactions` | CRUD, stats, summarize |
| Assistant | `/api/v1/assistant` | parse, voice upload |
| Health | `/health` | liveness, readiness |

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Commit changes (`git commit -m 'feat: add my feature'`)
4. Push to the branch (`git push origin feature/my-feature`)
5. Open a Pull Request

---

## License

Copyright © 2026 HCP CRM Module. All rights reserved.

This software is proprietary and confidential. Unauthorized copying, distribution, modification, or use of this software, via any medium, is strictly prohibited without explicit written permission from the copyright holder.

For licensing inquiries, please contact the repository owner.

---

<p align="center">
  Built with ❤️ for healthcare sales teams
</p>
