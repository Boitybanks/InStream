#!/usr/bin/env bash
# --pool=solo is required on Windows; Celery's default prefork pool needs
# os.fork(), which Windows doesn't have.
set -euo pipefail
cd "$(dirname "$0")/.."
uv run --package instream-worker celery -A instream_worker.celery_app worker --pool=solo --loglevel=info
