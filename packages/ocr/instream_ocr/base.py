from __future__ import annotations

from typing import Protocol

from instream_shared.types import OCRResult


class OCRProvider(Protocol):
    def extract_text(self, image_bytes: bytes, *, filename: str = "") -> OCRResult: ...
