#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
uv run --package instream-api uvicorn instream_api.main:app --reload --port 8000
