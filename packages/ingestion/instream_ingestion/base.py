from __future__ import annotations

from typing import Protocol

from instream_shared.types import RawContent


class AttachmentExtractor(Protocol):
    def extract(self, filename: str, content: bytes) -> RawContent: ...
