from __future__ import annotations

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from instream_auth import get_current_tenant
from instream_db.models import AuditEventRow, WorkflowRun
from instream_shared.types import WorkflowState
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.orm import Session

from instream_api.deps import get_db

router = APIRouter()


class WorkflowRunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email_id: uuid.UUID
    state: WorkflowState
    started_at: datetime
    completed_at: datetime | None


class AuditEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    event_type: str
    payload_json: dict
    occurred_at: datetime


def _get_owned_run(db: Session, run_id: uuid.UUID, tenant_id: uuid.UUID) -> WorkflowRun:
    run = db.get(WorkflowRun, run_id)
    if run is None or run.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Workflow run not found")
    return run


@router.get("", response_model=list[WorkflowRunResponse])
def list_workflow_runs(
    tenant_id: uuid.UUID = Depends(get_current_tenant), db: Session = Depends(get_db)
) -> list[WorkflowRun]:
    return list(
        db.scalars(
            select(WorkflowRun).where(WorkflowRun.tenant_id == tenant_id).order_by(WorkflowRun.started_at.desc())
        ).all()
    )


@router.get("/{run_id}", response_model=WorkflowRunResponse)
def get_workflow_run(
    run_id: uuid.UUID, tenant_id: uuid.UUID = Depends(get_current_tenant), db: Session = Depends(get_db)
) -> WorkflowRun:
    return _get_owned_run(db, run_id, tenant_id)


@router.get("/{run_id}/audit", response_model=list[AuditEventResponse])
def get_workflow_run_audit(
    run_id: uuid.UUID, tenant_id: uuid.UUID = Depends(get_current_tenant), db: Session = Depends(get_db)
) -> list[AuditEventRow]:
    _get_owned_run(db, run_id, tenant_id)
    return list(
        db.scalars(
            select(AuditEventRow)
            .where(AuditEventRow.workflow_run_id == run_id)
            .order_by(AuditEventRow.occurred_at)
        ).all()
    )
