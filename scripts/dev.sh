#!/usr/bin/env bash
set -euo pipefail

echo "==> Starting AI CRM development environment"
docker compose up --build "$@"
