from __future__ import annotations

import uuid
from datetime import date

from instream_db.models import AnalyticsDaily, AuditEventRow, WorkflowRun
from instream_shared.types import WorkflowState
from sqlalchemy import func, select
from sqlalchemy.orm import Session

_HUMAN_REVIEW_STATES = {WorkflowState.ROUTED_REVIEW, WorkflowState.ROUTED_INVALID}


def compute_daily_rollup(session: Session, *, tenant_id: uuid.UUID, for_date: date) -> AnalyticsDaily:
    """Recompute (and upsert) the analytics_daily row for one tenant/day from
    the underlying workflow_runs + audit_events — this is a rollup, not a
    source of truth, so it's always safe to recompute."""

    runs = session.scalars(
        select(WorkflowRun).where(
            WorkflowRun.tenant_id == tenant_id,
            func.date(WorkflowRun.started_at) == for_date,
        )
    ).all()

    processed = len(runs)
    completed = [r for r in runs if r.state == WorkflowState.COMPLETED and r.completed_at is not None]
    automated = sum(1 for r in runs if r.state not in _HUMAN_REVIEW_STATES)
    human_intervention = sum(1 for r in runs if r.state in _HUMAN_REVIEW_STATES)
    durations = [
        (r.completed_at - r.started_at).total_seconds() for r in completed if r.completed_at is not None
    ]
    avg_seconds = sum(durations) / len(durations) if durations else 0.0

    row = session.scalar(
        select(AnalyticsDaily).where(AnalyticsDaily.tenant_id == tenant_id, AnalyticsDaily.date == for_date)
    )
    if row is None:
        row = AnalyticsDaily(tenant_id=tenant_id, date=for_date)
        session.add(row)

    row.processed_count = processed
    row.automated_count = automated
    row.human_intervention_count = human_intervention
    row.avg_processing_seconds = avg_seconds
    row.sla_breaches = 0
    session.flush()
    return row


def summary(session: Session, *, tenant_id: uuid.UUID, start: date, end: date) -> dict:
    rows = session.scalars(
        select(AnalyticsDaily).where(
            AnalyticsDaily.tenant_id == tenant_id,
            AnalyticsDaily.date >= start,
            AnalyticsDaily.date <= end,
        )
    ).all()

    total_processed = sum(r.processed_count for r in rows)
    total_automated = sum(r.automated_count for r in rows)
    automation_rate = (total_automated / total_processed) if total_processed else 0.0

    exception_count = session.scalar(
        select(func.count())
        .select_from(AuditEventRow)
        .where(AuditEventRow.tenant_id == tenant_id, AuditEventRow.event_type == "workflow.exception")
    ) or 0

    return {
        "start": start.isoformat(),
        "end": end.isoformat(),
        "processed_count": total_processed,
        "automation_rate": round(automation_rate, 4),
        "human_intervention_count": sum(r.human_intervention_count for r in rows),
        "avg_processing_seconds": round(
            sum(r.avg_processing_seconds for r in rows) / len(rows), 2
        ) if rows else 0.0,
        "sla_breaches": sum(r.sla_breaches for r in rows),
        "exception_count": exception_count,
    }
