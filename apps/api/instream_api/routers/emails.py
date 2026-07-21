from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from instream_auth import get_current_tenant
from instream_db.models import Email
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.orm import Session

from instream_api.celery_client import celery_client
from instream_api.deps import get_db

router = APIRouter()


class EmailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    inbox_id: uuid.UUID
    sender: str
    subject: str
    status: str


@router.get("", response_model=list[EmailResponse])
def list_emails(
    tenant_id: uuid.UUID = Depends(get_current_tenant), db: Session = Depends(get_db)
) -> list[Email]:
    return list(db.scalars(select(Email).where(Email.tenant_id == tenant_id)).all())


@router.get("/{email_id}", response_model=EmailResponse)
def get_email(
    email_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant),
    db: Session = Depends(get_db),
) -> Email:
    email = db.get(Email, email_id)
    if email is None or email.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Email not found")
    return email


@router.post("/{email_id}/reprocess", status_code=202)
def reprocess_email(
    email_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant),
    db: Session = Depends(get_db),
) -> dict:
    email = db.get(Email, email_id)
    if email is None or email.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Email not found")
    celery_client.send_task("instream_worker.tasks.reprocess_email_task", args=[str(tenant_id), str(email_id)])
    return {"queued": True}
