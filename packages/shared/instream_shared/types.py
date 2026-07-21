"""Common value types shared across every package.

These are plain, storage-agnostic types — SQLAlchemy models in `instream-db`
persist them, but no package here should import an ORM.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class WorkflowState(StrEnum):
    RECEIVED = "RECEIVED"
    CLASSIFIED = "CLASSIFIED"
    VALIDATED = "VALIDATED"
    ROUTED_VALID = "ROUTED_VALID"
    ROUTED_INVALID = "ROUTED_INVALID"
    ROUTED_REVIEW = "ROUTED_REVIEW"
    COMPLETED = "COMPLETED"


class ValidationStatus(StrEnum):
    PASS_ = "PASS"
    FAIL = "FAIL"
    WARN = "WARN"


class Role(StrEnum):
    ADMIN = "admin"
    OPERATOR = "operator"
    REVIEWER = "reviewer"
    VIEWER = "viewer"


@dataclass(frozen=True)
class EmailAttachmentRef:
    filename: str
    mime_type: str
    content: bytes


@dataclass(frozen=True)
class EmailMessage:
    """A normalized email, independent of which EmailConnector fetched it."""

    message_id: str
    sender: str
    subject: str
    body: str
    received_at: datetime
    attachments: list[EmailAttachmentRef] = field(default_factory=list)


@dataclass(frozen=True)
class RawContent:
    """Output of an AttachmentExtractor: plain text plus a hint for OCR."""

    text: str
    needs_ocr: bool
    page_images: list[bytes] = field(default_factory=list)


@dataclass(frozen=True)
class OCRResult:
    text: str
    confidence: float
    provider: str
    layout: dict | None = None


@dataclass(frozen=True)
class ClassificationResult:
    doc_type: str
    confidence: float
    model: str
    fields: dict = field(default_factory=dict)


@dataclass(frozen=True)
class ExtractedField:
    value: str
    confidence: float


@dataclass(frozen=True)
class ValidationResult:
    rule_id: str
    rule_version: int
    status: ValidationStatus
    message: str


@dataclass(frozen=True)
class ConfidenceResult:
    score: float
    breakdown: dict[str, float]


@dataclass(frozen=True)
class AuditEvent:
    event_type: str
    payload: dict
    occurred_at: datetime = field(default_factory=utcnow)
