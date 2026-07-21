from __future__ import annotations

import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from instream_shared.tenant import set_current_tenant_id
from instream_shared.types import Role

from instream_auth.jwt import TokenService
from instream_auth.rbac import ROLE_ORDER

_bearer = HTTPBearer()
_token_service = TokenService()


def get_current_claims(credentials: HTTPAuthorizationCredentials = Depends(_bearer)) -> dict:
    try:
        return _token_service.verify(credentials.credentials)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token"
        ) from exc


def get_current_tenant(claims: dict = Depends(get_current_claims)) -> uuid.UUID:
    tenant_id = uuid.UUID(claims["tenant_id"])
    set_current_tenant_id(str(tenant_id))
    return tenant_id


def get_current_user_id(claims: dict = Depends(get_current_claims)) -> uuid.UUID:
    return uuid.UUID(claims["sub"])


def require_role(minimum: Role):
    def _dependency(claims: dict = Depends(get_current_claims)) -> Role:
        role = Role(claims["role"])
        if ROLE_ORDER[role] < ROLE_ORDER[minimum]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
        return role

    return _dependency
