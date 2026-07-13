# AI CRM - Root Dockerfile (Backend API)
# Builds the FastAPI backend from the repository root.
#
# Usage:
#   docker build -f Dockerfile --target production -t ai-crm-backend .
#   docker run -p 8000:8000 --env-file .env ai-crm-backend
#
# For full stack, use: docker compose up

FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# -----------------------------------------------------------------------------
# Dependencies
# -----------------------------------------------------------------------------
FROM base AS dependencies

COPY backend/requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# -----------------------------------------------------------------------------
# Development
# -----------------------------------------------------------------------------
FROM dependencies AS development

COPY backend/ .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# -----------------------------------------------------------------------------
# Production
# -----------------------------------------------------------------------------
FROM dependencies AS production

COPY backend/ .

RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["gunicorn", "app.main:app", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000", "-w", "4"]
