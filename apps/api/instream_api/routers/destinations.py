from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from instream_auth import get_current_tenant, require_role
from instream_db.models import Destination
from instream_db.session import engine
from instream_destinations import get_destination
from instream_shared.errors import InStreamError
from instream_shared.types import Role
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.orm import Session

from instream_api.deps import get_db

router = APIRouter()


class DestinationCreateRequest(BaseModel):
    type: str
    config: dict = {}


class DestinationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    type: str
    config_json: dict
    status: str


def _get_owned_destination(db: Session, destination_id: uuid.UUID, tenant_id: uuid.UUID) -> Destination:
    destination = db.get(Destination, destination_id)
    if destination is None or destination.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Destination not found")
    return destination


@router.get("", response_model=list[DestinationResponse])
def list_destinations(
    tenant_id: uuid.UUID = Depends(get_current_tenant), db: Session = Depends(get_db)
) -> list[Destination]:
    return list(db.scalars(select(Destination).where(Destination.tenant_id == tenant_id)).all())


@router.post("", response_model=DestinationResponse)
def create_destination(
    payload: DestinationCreateRequest,
    tenant_id: uuid.UUID = Depends(get_current_tenant),
    _role: Role = Depends(require_role(Role.OPERATOR)),
    db: Session = Depends(get_db),
) -> Destination:
    destination = Destination(tenant_id=tenant_id, type=payload.type, config_json=payload.config)
    db.add(destination)
    db.flush()
    return destination


@router.get("/{destination_id}", response_model=DestinationResponse)
def get_destination_route(
    destination_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant),
    db: Session = Depends(get_db),
) -> Destination:
    return _get_owned_destination(db, destination_id, tenant_id)


@router.post("/{destination_id}/test-connection")
def test_destination_connection(
    destination_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant),
    db: Session = Depends(get_db),
) -> dict:
    destination = _get_owned_destination(db, destination_id, tenant_id)
    try:
        connector = get_destination(destination.type, destination.config_json, engine=engine)
        ok = connector.test_connection()
    except InStreamError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"ok": ok}
