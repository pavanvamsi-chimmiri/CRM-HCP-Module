#!/usr/bin/env bash
set -euo pipefail

echo "==> AI CRM - Project Setup"

# Copy environment file if not exists
if [ ! -f .env ]; then
  echo "==> Creating .env from .env.example"
  cp .env.example .env
  echo "    Please update .env with your configuration (especially GROQ_API_KEY)"
else
  echo "==> .env already exists, skipping"
fi

# Frontend dependencies
echo "==> Installing frontend dependencies"
cd frontend && npm install && cd ..

# Backend virtual environment
echo "==> Setting up Python virtual environment"
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
cd ..

echo ""
echo "==> Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Update .env with your GROQ_API_KEY and secrets"
echo "  2. Start with Docker:  npm run dev"
echo "  3. Or run locally:"
echo "       Backend:  cd backend && source .venv/bin/activate && uvicorn app.main:app --reload"
echo "       Frontend: cd frontend && npm run dev"
