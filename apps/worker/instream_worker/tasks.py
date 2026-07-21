from __future__ import annotations

import uuid

from instream_connectors import get_connector
from instream_db.models import Inbox
from instream_db.session import get_session

from instream_worker.celery_app import app
from instream_worker.pipeline import process_email


@app.task(name="instream_worker.tasks.process_inbox_task")
def process_inbox_task(tenant_id: str, inbox_id: str) -> int:
    """Poll one inbox and run every new message through the full pipeline."""
    with get_session() as session:
        inbox = session.get(Inbox, uuid.UUID(inbox_id))
        if inbox is None:
            return 0
        connector = get_connector(inbox.connector_type, inbox.config_json)
        messages = connector.fetch_new_messages()
        for message in messages:
            process_email(session, tenant_id=uuid.UUID(tenant_id), inbox_id=inbox.id, message=message)
            connector.mark_processed(message.message_id)
        return len(messages)


@app.task(name="instream_worker.tasks.reprocess_email_task")
def reprocess_email_task(tenant_id: str, email_id: str) -> None:
    """Placeholder for Phase 1 — re-running OCR/AI on an already-stored
    email's attachments needs a blob-storage re-fetch path that lands with
    the destinations/mapping work in a later phase."""


@app.task(name="instream_worker.tasks.reclassify_document_task")
def reclassify_document_task(tenant_id: str, document_id: str) -> None:
    """Placeholder for Phase 1 — see `reprocess_email_task`."""
