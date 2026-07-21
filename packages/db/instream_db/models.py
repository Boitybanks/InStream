from __future__ import annotations

import uuid
from datetime import date, datetime

from instream_shared.types import Role, ValidationStatus, WorkflowState
from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from instream_db.base import Base, IdMixin, TenantScopedMixin, TimestampMixin, utcnow


class Tenant(Base, IdMixin, TimestampMixin):
    __tablename__ = "tenants"

    name: Mapped[str] = mapped_column(String(200))
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    status: Mapped[str] = mapped_column(String(30), default="active")


class Customer(Base, TenantScopedMixin):
    __tablename__ = "customers"

    name: Mapped[str] = mapped_column(String(200))


class CustomerPack(Base, TenantScopedMixin):
    __tablename__ = "customer_packs"

    name: Mapped[str] = mapped_column(String(100), index=True)
    version: Mapped[str] = mapped_column(String(30))
    manifest_path: Mapped[str] = mapped_column(String(500))
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    installed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class User(Base, TenantScopedMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[Role] = mapped_column(Enum(Role, name="user_role"), default=Role.VIEWER)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class Inbox(Base, TenantScopedMixin):
    __tablename__ = "inboxes"

    connector_type: Mapped[str] = mapped_column(String(50))
    config_json: Mapped[dict] = mapped_column(JSON, default=dict)
    status: Mapped[str] = mapped_column(String(30), default="active")


class Email(Base, TenantScopedMixin):
    __tablename__ = "emails"

    inbox_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("inboxes.id"), index=True)
    message_id: Mapped[str] = mapped_column(String(500), index=True)
    sender: Mapped[str] = mapped_column(String(320))
    subject: Mapped[str] = mapped_column(String(998), default="")
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    raw_ref: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(30), default="received")

    attachments: Mapped[list["Attachment"]] = relationship(back_populates="email")


class Attachment(Base, TenantScopedMixin):
    __tablename__ = "attachments"

    email_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("emails.id"), index=True)
    filename: Mapped[str] = mapped_column(String(500))
    mime_type: Mapped[str] = mapped_column(String(150))
    storage_ref: Mapped[str] = mapped_column(String(255))
    size: Mapped[int] = mapped_column(Integer, default=0)

    email: Mapped["Email"] = relationship(back_populates="attachments")


class Document(Base, TenantScopedMixin):
    __tablename__ = "documents"

    attachment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("attachments.id"), index=True
    )
    extracted_text_ref: Mapped[str] = mapped_column(String(255))
    ocr_provider: Mapped[str] = mapped_column(String(50), default="mock")
    ocr_confidence: Mapped[float] = mapped_column(Float, default=0.0)


class Classification(Base, TenantScopedMixin):
    __tablename__ = "classifications"

    document_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("documents.id"), index=True)
    doc_type: Mapped[str] = mapped_column(String(100))
    confidence: Mapped[float] = mapped_column(Float)
    model: Mapped[str] = mapped_column(String(100))


class Rule(Base, TenantScopedMixin):
    __tablename__ = "rules"

    customer_pack_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("customer_packs.id"), index=True, nullable=True
    )
    key: Mapped[str] = mapped_column(String(150), index=True)
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text, default="")

    versions: Mapped[list["RuleVersion"]] = relationship(back_populates="rule")


class RuleVersion(Base, IdMixin):
    __tablename__ = "rule_versions"

    rule_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("rules.id"), index=True)
    version: Mapped[int] = mapped_column(Integer)
    definition_yaml: Mapped[str] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    rule: Mapped["Rule"] = relationship(back_populates="versions")


class ValidationResultRow(Base, TenantScopedMixin):
    __tablename__ = "validation_results"

    document_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("documents.id"), index=True)
    # Nullable: a pack's rules can be evaluated straight from YAML before
    # they've been published through the /rules API into a RuleVersion row.
    rule_version_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("rule_versions.id"), index=True, nullable=True
    )
    status: Mapped[ValidationStatus] = mapped_column(Enum(ValidationStatus, name="validation_status"))
    message: Mapped[str] = mapped_column(Text, default="")
    evaluated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class ConfidenceScoreRow(Base, TenantScopedMixin):
    __tablename__ = "confidence_scores"

    subject_type: Mapped[str] = mapped_column(String(50))
    subject_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    score: Mapped[float] = mapped_column(Float)
    breakdown_json: Mapped[dict] = mapped_column(JSON, default=dict)


class WorkflowRun(Base, TenantScopedMixin):
    __tablename__ = "workflow_runs"

    email_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("emails.id"), index=True)
    state: Mapped[WorkflowState] = mapped_column(
        Enum(WorkflowState, name="workflow_state"), default=WorkflowState.RECEIVED
    )
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    audit_events: Mapped[list["AuditEventRow"]] = relationship(back_populates="workflow_run")


class AuditEventRow(Base, TenantScopedMixin):
    """Insert-only. No route or service in this codebase should UPDATE or DELETE
    a row here — that invariant is what makes the audit trail trustworthy."""

    __tablename__ = "audit_events"

    workflow_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workflow_runs.id"), index=True
    )
    event_type: Mapped[str] = mapped_column(String(100))
    payload_json: Mapped[dict] = mapped_column(JSON, default=dict)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    workflow_run: Mapped["WorkflowRun"] = relationship(back_populates="audit_events")


class Destination(Base, TenantScopedMixin):
    __tablename__ = "destinations"

    type: Mapped[str] = mapped_column(String(50))
    config_json: Mapped[dict] = mapped_column(JSON, default=dict)
    status: Mapped[str] = mapped_column(String(30), default="active")


class Notification(Base, TenantScopedMixin):
    __tablename__ = "notifications"

    workflow_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workflow_runs.id"), index=True
    )
    channel: Mapped[str] = mapped_column(String(50))
    template: Mapped[str] = mapped_column(String(150))
    status: Mapped[str] = mapped_column(String(30), default="pending")
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class AnalyticsDaily(Base, TenantScopedMixin):
    __tablename__ = "analytics_daily"

    date: Mapped[date] = mapped_column(Date, index=True)
    processed_count: Mapped[int] = mapped_column(Integer, default=0)
    automated_count: Mapped[int] = mapped_column(Integer, default=0)
    human_intervention_count: Mapped[int] = mapped_column(Integer, default=0)
    avg_processing_seconds: Mapped[float] = mapped_column(Float, default=0.0)
    sla_breaches: Mapped[int] = mapped_column(Integer, default=0)
