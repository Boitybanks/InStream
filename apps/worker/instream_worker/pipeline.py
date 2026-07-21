"""The core ingestion -> OCR -> classification -> validation -> workflow
pipeline, as a plain function independent of Celery. Celery tasks in
`tasks.py` are thin wrappers around this so the pipeline itself stays
directly unit-testable (no broker required).
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from instream_ai import get_ai_provider
from instream_ai.base import AIProvider
from instream_audit import AuditLogger
from instream_confidence import ConfidenceEngine
from instream_db.models import (
    Attachment,
    Classification,
    ConfidenceScoreRow,
    Destination,
    Document,
    Email,
    Rule,
    RuleVersion,
    ValidationResultRow,
    WorkflowRun,
)
from instream_destinations import get_destination
from instream_ingestion import extract_attachment
from instream_ocr import get_ocr_provider
from instream_ocr.base import OCRProvider
from instream_rules import RuleDefinition, RulesEngine
from instream_shared.storage import BlobStorage, LocalFileStorage
from instream_shared.types import EmailMessage, WorkflowState
from instream_workflow import WorkflowEngine
from sqlalchemy import select
from sqlalchemy.orm import Session


def _resolve_rule_version_id(
    session: Session, tenant_id: uuid.UUID, rule_key: str, version: int
) -> uuid.UUID | None:
    return session.scalar(
        select(RuleVersion.id)
        .join(Rule, Rule.id == RuleVersion.rule_id)
        .where(Rule.tenant_id == tenant_id, Rule.key == rule_key, RuleVersion.version == version)
    )


def process_email(
    session: Session,
    *,
    tenant_id: uuid.UUID,
    inbox_id: uuid.UUID,
    message: EmailMessage,
    rules: list[RuleDefinition] | None = None,
    confidence_thresholds: dict[str, float] | None = None,
    destination: Destination | None = None,
    storage: BlobStorage | None = None,
    ocr: OCRProvider | None = None,
    ai: AIProvider | None = None,
) -> WorkflowRun:
    storage = storage or LocalFileStorage()
    ocr = ocr or get_ocr_provider()
    ai = ai or get_ai_provider()
    rules_engine = RulesEngine()
    workflow_engine = WorkflowEngine()
    confidence_engine = ConfidenceEngine()
    audit = AuditLogger(session)

    raw_ref = storage.put(message.body.encode("utf-8"), suffix=".eml")
    email_row = Email(
        tenant_id=tenant_id,
        inbox_id=inbox_id,
        message_id=message.message_id,
        sender=message.sender,
        subject=message.subject,
        received_at=message.received_at,
        raw_ref=raw_ref,
        status="processing",
    )
    session.add(email_row)
    session.flush()

    run = WorkflowRun(tenant_id=tenant_id, email_id=email_row.id, state=WorkflowState.RECEIVED)
    session.add(run)
    session.flush()
    audit.record(
        tenant_id=tenant_id,
        workflow_run_id=run.id,
        event_type="email.received",
        payload={"message_id": message.message_id, "sender": message.sender},
    )

    all_validation_results = []
    field_scores: dict[str, float] = {}

    for attachment in message.attachments:
        attachment_ref = storage.put(attachment.content, suffix=f"_{attachment.filename}")
        attachment_row = Attachment(
            tenant_id=tenant_id,
            email_id=email_row.id,
            filename=attachment.filename,
            mime_type=attachment.mime_type,
            storage_ref=attachment_ref,
            size=len(attachment.content),
        )
        session.add(attachment_row)
        session.flush()

        raw_content = extract_attachment(attachment.filename, attachment.content)
        text = raw_content.text
        ocr_confidence = 1.0
        if raw_content.needs_ocr:
            ocr_result = ocr.extract_text(attachment.content, filename=attachment.filename)
            text = ocr_result.text
            ocr_confidence = ocr_result.confidence

        text_ref = storage.put(text.encode("utf-8"), suffix=".txt")
        document_row = Document(
            tenant_id=tenant_id,
            attachment_id=attachment_row.id,
            extracted_text_ref=text_ref,
            ocr_provider="mock",
            ocr_confidence=ocr_confidence,
        )
        session.add(document_row)
        session.flush()

        classification = ai.classify_document(text)
        session.add(
            Classification(
                tenant_id=tenant_id,
                document_id=document_row.id,
                doc_type=classification.doc_type,
                confidence=classification.confidence,
                model=classification.model,
            )
        )
        session.flush()

        field_scores[f"{attachment.filename}:ocr"] = ocr_confidence
        field_scores[f"{attachment.filename}:classification"] = classification.confidence

        context = {"doc_type": classification.doc_type, "document": {"age_days": 0}}
        results = rules_engine.evaluate(context, rules or [])
        for result in results:
            rule_version_id = _resolve_rule_version_id(session, tenant_id, result.rule_id, result.rule_version)
            session.add(
                ValidationResultRow(
                    tenant_id=tenant_id,
                    document_id=document_row.id,
                    rule_version_id=rule_version_id,
                    status=result.status,
                    message=result.message,
                )
            )
            all_validation_results.append(result)
        session.flush()

    run.state = workflow_engine.transition(run.state, WorkflowState.CLASSIFIED)
    audit.record(tenant_id=tenant_id, workflow_run_id=run.id, event_type="workflow.classified", payload={})

    run.state = workflow_engine.transition(run.state, WorkflowState.VALIDATED)
    audit.record(
        tenant_id=tenant_id,
        workflow_run_id=run.id,
        event_type="workflow.validated",
        payload={"result_count": len(all_validation_results)},
    )

    confidence_result = confidence_engine.score(field_scores)
    session.add(
        ConfidenceScoreRow(
            tenant_id=tenant_id,
            subject_type="workflow_run",
            subject_id=run.id,
            score=confidence_result.score,
            breakdown_json=confidence_result.breakdown,
        )
    )
    confidence_label = confidence_engine.classify(confidence_result.score, confidence_thresholds)

    next_state = workflow_engine.route(all_validation_results, confidence_label)
    run.state = workflow_engine.transition(run.state, next_state)
    audit.record(
        tenant_id=tenant_id,
        workflow_run_id=run.id,
        event_type="workflow.routed",
        payload={"state": run.state.value, "confidence": confidence_result.score},
    )
    if run.state == WorkflowState.ROUTED_INVALID:
        audit.record(
            tenant_id=tenant_id,
            workflow_run_id=run.id,
            event_type="workflow.exception",
            payload={"reason": "rule_failure"},
        )

    if destination is not None and run.state == WorkflowState.ROUTED_VALID:
        connector = get_destination(destination.type, destination.config_json)
        connector.write(
            {
                "email_id": str(email_row.id),
                "sender": email_row.sender,
                "subject": email_row.subject,
                "confidence": confidence_result.score,
            }
        )
        audit.record(
            tenant_id=tenant_id, workflow_run_id=run.id, event_type="destination.written", payload={}
        )

    run.completed_at = datetime.now(timezone.utc)
    run.state = workflow_engine.transition(run.state, WorkflowState.COMPLETED)
    email_row.status = "completed"
    audit.record(tenant_id=tenant_id, workflow_run_id=run.id, event_type="workflow.completed", payload={})

    session.flush()
    return run
