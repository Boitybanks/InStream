"""Ambient tenant context.

Every request (API) and every task (worker) runs on behalf of exactly one
tenant. Rather than threading a `tenant_id` argument through every function
signature in every package, we set it once at the entrypoint (an auth
dependency, a Celery task wrapper) and read it wherever it's needed — most
importantly in `instream-db`, which uses it to scope every query.
"""
from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar

from instream_shared.errors import InStreamError

_current_tenant_id: ContextVar[str | None] = ContextVar("_current_tenant_id", default=None)


class NoTenantContextError(InStreamError):
    """Raised when tenant-scoped code runs without a tenant having been set."""


def get_current_tenant_id() -> str:
    tenant_id = _current_tenant_id.get()
    if tenant_id is None:
        raise NoTenantContextError("No tenant is set on the current context")
    return tenant_id


def set_current_tenant_id(tenant_id: str) -> None:
    _current_tenant_id.set(tenant_id)


@contextmanager
def tenant_context(tenant_id: str):
    token = _current_tenant_id.set(tenant_id)
    try:
        yield
    finally:
        _current_tenant_id.reset(token)
