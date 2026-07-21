from __future__ import annotations

import os
import time
import uuid

import jwt

JWT_SECRET = os.environ.get("JWT_SECRET", "dev-only-change-me")
JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM", "HS256")
JWT_EXPIRES_MINUTES = int(os.environ.get("JWT_EXPIRES_MINUTES", "60"))


class TokenService:
    def issue(self, *, user_id: uuid.UUID, tenant_id: uuid.UUID, role: str) -> str:
        now = int(time.time())
        payload = {
            "sub": str(user_id),
            "tenant_id": str(tenant_id),
            "role": role,
            "iat": now,
            "exp": now + JWT_EXPIRES_MINUTES * 60,
        }
        return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    def verify(self, token: str) -> dict:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
