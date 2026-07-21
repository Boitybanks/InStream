from __future__ import annotations

from fastapi import FastAPI

from instream_api.routers import (
    analytics,
    auth,
    destinations,
    documents,
    emails,
    health,
    inboxes,
    rules,
    tenants,
    workflow_runs,
)

app = FastAPI(title="inStream API", version="0.1.0")

app.include_router(health.router)
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(tenants.router, prefix="/tenants", tags=["tenants"])
app.include_router(inboxes.router, prefix="/inboxes", tags=["inboxes"])
app.include_router(emails.router, prefix="/emails", tags=["emails"])
app.include_router(documents.router, prefix="/documents", tags=["documents"])
app.include_router(rules.router, prefix="/rules", tags=["rules"])
app.include_router(workflow_runs.router, prefix="/workflow-runs", tags=["workflow-runs"])
app.include_router(destinations.router, prefix="/destinations", tags=["destinations"])
app.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
