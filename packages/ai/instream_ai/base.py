from __future__ import annotations

from typing import Protocol

from instream_shared.types import ClassificationResult, ExtractedField


class AIProvider(Protocol):
    """AI is used only for reasoning — classification confidence, summaries,
    drafted text, and extracted field candidates. It never emits a PASS/FAIL
    verdict; that authority belongs solely to the Rules Engine.
    """

    def classify_document(self, text: str, *, candidate_types: list[str] | None = None) -> ClassificationResult: ...

    def summarize(self, text: str) -> str: ...

    def draft_email(self, context: dict) -> str: ...

    def extract_fields(self, text: str, doc_type: str) -> dict[str, ExtractedField]: ...
