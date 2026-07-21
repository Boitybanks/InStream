from __future__ import annotations

import uuid

import yaml
from fastapi import APIRouter, Depends, HTTPException
from instream_auth import get_current_tenant, require_role
from instream_db.models import Rule, RuleVersion
from instream_rules import RuleDefinition
from instream_shared.errors import ConfigError
from instream_shared.types import Role
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.orm import Session

from instream_api.deps import get_db

router = APIRouter()


class RuleCreateRequest(BaseModel):
    key: str
    name: str
    description: str = ""


class RuleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    key: str
    name: str
    description: str


class RuleVersionCreateRequest(BaseModel):
    definition_yaml: str


class RuleVersionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    version: int
    definition_yaml: str
    is_active: bool


def _get_owned_rule(db: Session, rule_id: uuid.UUID, tenant_id: uuid.UUID) -> Rule:
    rule = db.get(Rule, rule_id)
    if rule is None or rule.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Rule not found")
    return rule


@router.get("", response_model=list[RuleResponse])
def list_rules(tenant_id: uuid.UUID = Depends(get_current_tenant), db: Session = Depends(get_db)) -> list[Rule]:
    return list(db.scalars(select(Rule).where(Rule.tenant_id == tenant_id)).all())


@router.post("", response_model=RuleResponse)
def create_rule(
    payload: RuleCreateRequest,
    tenant_id: uuid.UUID = Depends(get_current_tenant),
    _role: Role = Depends(require_role(Role.OPERATOR)),
    db: Session = Depends(get_db),
) -> Rule:
    rule = Rule(tenant_id=tenant_id, key=payload.key, name=payload.name, description=payload.description)
    db.add(rule)
    db.flush()
    return rule


@router.get("/{rule_id}", response_model=RuleResponse)
def get_rule(
    rule_id: uuid.UUID, tenant_id: uuid.UUID = Depends(get_current_tenant), db: Session = Depends(get_db)
) -> Rule:
    return _get_owned_rule(db, rule_id, tenant_id)


@router.get("/{rule_id}/versions", response_model=list[RuleVersionResponse])
def list_rule_versions(
    rule_id: uuid.UUID, tenant_id: uuid.UUID = Depends(get_current_tenant), db: Session = Depends(get_db)
) -> list[RuleVersion]:
    _get_owned_rule(db, rule_id, tenant_id)
    return list(
        db.scalars(select(RuleVersion).where(RuleVersion.rule_id == rule_id).order_by(RuleVersion.version)).all()
    )


@router.post("/{rule_id}/versions", response_model=RuleVersionResponse)
def create_rule_version(
    rule_id: uuid.UUID,
    payload: RuleVersionCreateRequest,
    tenant_id: uuid.UUID = Depends(get_current_tenant),
    _role: Role = Depends(require_role(Role.OPERATOR)),
    db: Session = Depends(get_db),
) -> RuleVersion:
    _get_owned_rule(db, rule_id, tenant_id)
    try:
        RuleDefinition.model_validate(yaml.safe_load(payload.definition_yaml))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid rule definition: {exc}") from exc

    latest = db.scalar(
        select(RuleVersion).where(RuleVersion.rule_id == rule_id).order_by(RuleVersion.version.desc())
    )
    next_version = (latest.version + 1) if latest else 1
    version = RuleVersion(rule_id=rule_id, version=next_version, definition_yaml=payload.definition_yaml)
    db.add(version)
    db.flush()
    return version


@router.post("/{rule_id}/versions/{version_id}/publish", response_model=RuleVersionResponse)
def publish_rule_version(
    rule_id: uuid.UUID,
    version_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant),
    _role: Role = Depends(require_role(Role.OPERATOR)),
    db: Session = Depends(get_db),
) -> RuleVersion:
    _get_owned_rule(db, rule_id, tenant_id)
    target = db.get(RuleVersion, version_id)
    if target is None or target.rule_id != rule_id:
        raise HTTPException(status_code=404, detail="Rule version not found")

    all_versions = db.scalars(select(RuleVersion).where(RuleVersion.rule_id == rule_id)).all()
    for version in all_versions:
        version.is_active = version.id == target.id
    db.flush()
    return target
