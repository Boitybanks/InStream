from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from instream_auth import TokenService, verify_password
from instream_db.models import User
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from instream_api.deps import get_db

router = APIRouter()
_token_service = TokenService()


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    # Phase 1 treats email as a unique login identifier; per-tenant email
    # uniqueness (same address across two tenants) is a later-phase concern.
    user = db.scalar(select(User).where(User.email == payload.email))
    if user is None or not user.is_active or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = _token_service.issue(user_id=user.id, tenant_id=user.tenant_id, role=user.role.value)
    return TokenResponse(access_token=token)
