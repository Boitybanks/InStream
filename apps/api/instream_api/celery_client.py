"""A Celery *client* — sends tasks by name over Redis without importing the
worker app's code, so `apps/api` and `apps/worker` stay independently
deployable."""
from __future__ import annotations

import os

from celery import Celery

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
celery_client = Celery("instream-api-client", broker=REDIS_URL, backend=REDIS_URL)
