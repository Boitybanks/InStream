"""Bootstrap the first tenant + admin user for local development.

New tenant onboarding isn't exposed over the API in Phase 1 (see
`apps/api/instream_api/routers/tenants.py`) — this script is the supported
way to create one until a proper multi-tenant admin console exists.

Usage: uv run --package instream-api python scripts/seed.py
"""
from __future__ import annotations

from instream_auth import hash_password
from instream_db.base import Base
from instream_db.models import Tenant, User
from instream_db.session import SessionLocal, engine
from instream_shared.types import Role

TENANT_SLUG = "acme-dev"
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "changeme123"  # noqa: S105 — local dev seed only


def main() -> None:
    Base.metadata.create_all(engine)

    with SessionLocal() as session:
        tenant = session.query(Tenant).filter_by(slug=TENANT_SLUG).one_or_none()
        if tenant is None:
            tenant = Tenant(name="Acme Dev Tenant", slug=TENANT_SLUG, status="active")
            session.add(tenant)
            session.flush()
            print(f"Created tenant {tenant.slug} ({tenant.id})")
        else:
            print(f"Tenant {tenant.slug} already exists ({tenant.id})")

        user = session.query(User).filter_by(email=ADMIN_EMAIL, tenant_id=tenant.id).one_or_none()
        if user is None:
            user = User(
                tenant_id=tenant.id,
                email=ADMIN_EMAIL,
                hashed_password=hash_password(ADMIN_PASSWORD),
                role=Role.ADMIN,
                is_active=True,
            )
            session.add(user)
            print(f"Created admin user {ADMIN_EMAIL} / {ADMIN_PASSWORD}")
        else:
            print(f"Admin user {ADMIN_EMAIL} already exists")

        session.commit()


if __name__ == "__main__":
    main()
