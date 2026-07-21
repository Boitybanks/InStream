from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from instream_auth import get_current_tenant, require_role
from instream_connectors import get_connector
from instream_db.models import Inbox
from instream_shared.errors import InStreamError
from instream_shared.types import Role
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.orm import Session

from instream_api.deps import get_db

router = APIRouter()


class InboxCreateRequest(BaseModel):
    connector_type: str
    config: dict = {}


class InboxResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    connector_type: str
    config_json: dict
    status: str


def _get_owned_inbox(db: Session, inbox_id: uuid.UUID, tenant_id: uuid.UUID) -> Inbox:
    inbox = db.get(Inbox, inbox_id)
    if inbox is None or inbox.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Inbox not found")
    return inbox


@router.get("", response_model=list[InboxResponse])
def list_inboxes(
    tenant_id: uuid.UUID = Depends(get_current_tenant), db: Session = Depends(get_db)
) -> list[Inbox]:
    return list(db.scalars(select(Inbox).where(Inbox.tenant_id == tenant_id)).all())


@router.post("", response_model=InboxResponse)
def create_inbox(
    payload: InboxCreateRequest,
    tenant_id: uuid.UUID = Depends(get_current_tenant),
    _role: Role = Depends(require_role(Role.OPERATOR)),
    db: Session = Depends(get_db),
) -> Inbox:
    inbox = Inbox(tenant_id=tenant_id, connector_type=payload.connector_type, config_json=payload.config)
    db.add(inbox)
    db.flush()
    return inbox


@router.get("/{inbox_id}", response_model=InboxResponse)
def get_inbox(
    inbox_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant),
    db: Session = Depends(get_db),
) -> Inbox:
    return _get_owned_inbox(db, inbox_id, tenant_id)


@router.delete("/{inbox_id}", status_code=204)
def delete_inbox(
    inbox_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant),
    _role: Role = Depends(require_role(Role.OPERATOR)),
    db: Session = Depends(get_db),
) -> None:
    inbox = _get_owned_inbox(db, inbox_id, tenant_id)
    db.delete(inbox)


@router.post("/{inbox_id}/test-connection")
def test_inbox_connection(
    inbox_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant),
    db: Session = Depends(get_db),
) -> dict:
    inbox = _get_owned_inbox(db, inbox_id, tenant_id)
    try:
        connector = get_connector(inbox.connector_type, inbox.config_json)
        ok = connector.test_connection()
    except InStreamError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"ok": ok}
