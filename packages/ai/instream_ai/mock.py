from __future__ import annotations

from instream_shared.types import ClassificationResult, ExtractedField

_KEYWORD_DOC_TYPES: dict[str, str] = {
    "bank statement": "bank_statement",
    "payslip": "payslip",
    "passport": "passport",
    "death certificate": "death_certificate",
    "proof of address": "proof_of_address",
    "court order": "court_order",
    "medical report": "medical_report",
}


class MockAIProvider:
    """Deterministic keyword-matching stand-in for a real LLM. Good enough to
    prove the pipeline end-to-end in Phase 1; `AnthropicProvider` and
    `OpenAIProvider` implement the same interface once real keys are
    supplied."""

    def classify_document(self, text: str, *, candidate_types: list[str] | None = None) -> ClassificationResult:
        lowered = text.lower()
        for keyword, doc_type in _KEYWORD_DOC_TYPES.items():
            if keyword in lowered:
                return ClassificationResult(doc_type=doc_type, confidence=0.9, model="mock")
        return ClassificationResult(doc_type="unknown", confidence=0.3, model="mock")

    def summarize(self, text: str) -> str:
        stripped = text.strip()
        if len(stripped) <= 200:
            return stripped
        return stripped[:197] + "..."

    def draft_email(self, context: dict) -> str:
        recipient = context.get("recipient_name", "there")
        reason = context.get("reason", "we need more information to process your request")
        return f"Hi {recipient},\n\n{reason}\n\nKind regards,\ninStream"

    def extract_fields(self, text: str, doc_type: str) -> dict[str, ExtractedField]:
        return {}
