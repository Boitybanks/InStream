from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from instream_auth import get_current_tenant, require_role
from instream_db.models import Tenant
from instream_shared.types import Role
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from instream_api.deps import get_db

router = APIRouter()


class TenantResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    slug: str
    status: str


class TenantUpdateRequest(BaseModel):
    name: str | None = None
    status: str | None = None


@router.get("", response_model=TenantResponse)
def get_my_tenant(
    tenant_id: uuid.UUID = Depends(get_current_tenant), db: Session = Depends(get_db)
) -> Tenant:
    """New tenant onboarding is a seeded/operational action in Phase 1 (see
    `scripts/seed.py`), not a public API — there's no authenticated identity
    to create a *first* tenant for. This endpoint only reads/updates the
    caller's own tenant."""
    return db.get(Tenant, tenant_id)


@router.patch("", response_model=TenantResponse)
def update_my_tenant(
    payload: TenantUpdateRequest,
    tenant_id: uuid.UUID = Depends(get_current_tenant),
    _role: Role = Depends(require_role(Role.ADMIN)),
    db: Session = Depends(get_db),
) -> Tenant:
    tenant = db.get(Tenant, tenant_id)
    if payload.name is not None:
        tenant.name = payload.name
    if payload.status is not None:
        tenant.status = payload.status
    db.flush()
    return tenant
