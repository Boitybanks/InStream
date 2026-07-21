from __future__ import annotations

from instream_shared.types import OCRResult


class MockOCRProvider:
    """Deterministic stand-in for a real OCR provider — same input, same
    output, every time. Good enough to prove the pipeline; not meant to
    read an actual scanned document."""

    def __init__(self, *, confidence: float = 0.95, canned_text: str = "") -> None:
        self._confidence = confidence
        self._canned_text = canned_text

    def extract_text(self, image_bytes: bytes, *, filename: str = "") -> OCRResult:
        text = self._canned_text or f"[mock-ocr text extracted from {filename or 'attachment'}]"
        return OCRResult(text=text, confidence=self._confidence, provider="mock")
