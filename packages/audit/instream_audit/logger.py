from __future__ import annotations

import uuid

from instream_db.models import AuditEventRow
from sqlalchemy.orm import Session


class AuditLogger:
    """Append-only by design: this class exposes exactly one write method,
    `record()` — there is no `update` or `delete`. (DB-level grant
    restrictions that make this unbypassable even from a raw SQL console
    are part of the hardened deployment in a later phase, not Phase 1.)
    """

    def __init__(self, session: Session) -> None:
        self._session = session

    def record(
        self,
        *,
        tenant_id: uuid.UUID,
        workflow_run_id: uuid.UUID,
        event_type: str,
        payload: dict | None = None,
    ) -> AuditEventRow:
        event = AuditEventRow(
            tenant_id=tenant_id,
            workflow_run_id=workflow_run_id,
            event_type=event_type,
            payload_json=payload or {},
        )
        self._session.add(event)
        self._session.flush()
        return event
