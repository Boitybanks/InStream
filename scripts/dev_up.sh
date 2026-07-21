#!/usr/bin/env bash
# Bring up local infra + apply migrations + seed a dev tenant. Run once
# after cloning, or any time you want a clean local environment.
set -euo pipefail
cd "$(dirname "$0")/.."

docker compose -f infra/docker-compose.yml up -d
uv sync
(cd packages/db && uv run --project ../.. alembic upgrade head)
uv run --package instream-api python scripts/seed.py

echo
echo "Ready. Log in with admin@example.com / changeme123 once the API is running:"
echo "  bash scripts/run_api.sh"
echo "  bash scripts/run_worker.sh"
echo "  pnpm dashboard:dev"
