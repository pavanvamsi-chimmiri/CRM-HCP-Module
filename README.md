# AI CRM

Enterprise-grade Customer Relationship Management platform powered by AI agents. Built with a modern React frontend and FastAPI backend, featuring LangGraph orchestration and Groq LLM integration.

## Tech Stack

### Frontend
| Technology | Purpose |
|------------|---------|
| React 18 | UI framework |
| Vite 6 | Build tool & dev server |
| TypeScript | Type safety |
| Redux Toolkit | State management |
| Tailwind CSS | Styling |
| React Router 7 | Client-side routing |
| Axios | HTTP client |

### Backend
| Technology | Purpose |
|------------|---------|
| FastAPI | REST API framework |
| SQLAlchemy 2 | ORM & database layer |
| PostgreSQL 16 | Primary database |
| Pydantic v2 | Data validation |
| LangGraph | AI agent orchestration |
| Groq API | LLM inference |
| Alembic | Database migrations |

## Project Structure

```
ai-crm/
├── frontend/                    # React + Vite application
│   ├── public/                  # Static assets
│   ├── src/
│   │   ├── app/                 # App-level providers & config
│   │   ├── assets/              # Images, fonts, global styles
│   │   ├── components/          # Shared UI components
│   │   │   ├── common/          # Reusable business components
│   │   │   ├── layout/          # Layout shells (sidebar, header)
│   │   │   └── ui/              # Primitive UI elements
│   │   ├── features/            # Feature-based modules
│   │   │   ├── auth/            # Authentication
│   │   │   ├── contacts/        # Contact management
│   │   │   ├── dashboard/       # Analytics dashboard
│   │   │   ├── deals/           # Pipeline & deals
│   │   │   └── ai-assistant/    # AI chat & insights
│   │   ├── hooks/               # Shared React hooks
│   │   ├── lib/                 # Third-party library wrappers
│   │   ├── pages/               # Route page components
│   │   ├── routes/              # Route definitions
│   │   ├── services/            # API service layer
│   │   ├── store/               # Redux store & slices
│   │   ├── types/               # TypeScript type definitions
│   │   └── utils/               # Utility functions
│   ├── Dockerfile
│   ├── package.json
│   └── vite.config.ts
│
├── backend/                     # FastAPI application
│   ├── app/
│   │   ├── api/                 # API layer
│   │   │   └── v1/              # API version 1
│   │   │       └── endpoints/   # Route handlers
│   │   ├── core/                # Config, security, logging
│   │   ├── db/                  # Database session & migrations
│   │   ├── models/              # SQLAlchemy ORM models
│   │   ├── schemas/             # Pydantic request/response schemas
│   │   ├── services/            # Business logic layer
│   │   ├── repositories/        # Data access layer
│   │   ├── ai/                  # AI agent subsystem
│   │   │   ├── graphs/          # LangGraph workflow definitions
│   │   │   ├── agents/          # Agent implementations
│   │   │   ├── prompts/         # System & task prompts
│   │   │   └── tools/           # Agent tools (CRM actions)
│   │   └── middleware/          # HTTP middleware
│   ├── alembic/                 # Database migration scripts
│   ├── tests/                   # Test suite
│   │   ├── unit/
│   │   └── integration/
│   ├── Dockerfile
│   └── requirements.txt
│
├── docs/                        # Documentation
├── scripts/                     # Dev & deployment scripts
├── .github/workflows/           # CI/CD pipelines
├── docker-compose.yml           # Multi-service orchestration
├── Dockerfile                   # Root backend production image
├── .env.example                 # Environment template
└── package.json                 # Monorepo scripts
```

## Prerequisites

- **Node.js** >= 20
- **Python** >= 3.11
- **Docker** & **Docker Compose**
- **PostgreSQL** 16 (or use Docker)
- **Groq API key** — [Get one here](https://console.groq.com/)

## Quick Start

### 1. Clone and configure

```bash
git clone <repository-url>
cd ai-crm
cp .env.example .env
# Edit .env — set GROQ_API_KEY and secrets
```

### 2. Run with Docker (recommended)

```bash
docker compose up --build
```

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| PostgreSQL | localhost:5432 |

### 3. Run locally (without Docker)

```bash
# Automated setup
bash scripts/setup.sh

# Terminal 1 — Backend
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 — Frontend
cd frontend
npm run dev
```

## Environment Variables

Copy `.env.example` to `.env` and configure:

| Variable | Description |
|----------|-------------|
| `GROQ_API_KEY` | Groq API key for LLM inference |
| `DATABASE_URL` | PostgreSQL connection string (async) |
| `JWT_SECRET_KEY` | Secret for JWT token signing |
| `APP_SECRET_KEY` | Application secret key |
| `VITE_API_BASE_URL` | Backend API URL for frontend |

See `.env.example` for the full list.

## Development

### Frontend commands

```bash
cd frontend
npm run dev          # Start dev server
npm run build        # Production build
npm run lint         # ESLint
npm run type-check   # TypeScript check
```

### Backend commands

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload    # Dev server
pytest                           # Run tests
ruff check app tests             # Lint
alembic upgrade head             # Run migrations
```

### Monorepo scripts (from root)

```bash
npm run dev              # Docker Compose up
npm run frontend:dev     # Frontend only
npm run setup            # Initial project setup
```

## Docker

### Development

```bash
docker compose up --build
```

### Production build

```bash
# Backend
docker build -f Dockerfile --target production -t ai-crm-backend .

# Frontend
docker build -f frontend/Dockerfile --target production -t ai-crm-frontend ./frontend
```

## Architecture

```
┌─────────────┐     HTTP/REST      ┌─────────────┐     SQL      ┌────────────┐
│   React     │ ◄───────────────► │   FastAPI   │ ◄──────────► │ PostgreSQL │
│  Frontend   │                    │   Backend   │              │            │
└─────────────┘                    └──────┬──────┘              └────────────┘
                                          │
                                          │ LangGraph
                                          ▼
                                   ┌─────────────┐
                                   │  Groq API   │
                                   │   (LLM)     │
                                   └─────────────┘
```

- **Feature-based frontend** — Modules colocate components, hooks, and services per domain.
- **Layered backend** — API → Services → Repositories → Models.
- **AI subsystem** — LangGraph agents with CRM-specific tools and Groq-powered inference.

## License

Proprietary — All rights reserved.
