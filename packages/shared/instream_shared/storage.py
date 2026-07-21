"""Blob storage abstraction.

Phase 1 ships a local-filesystem backend only. It exists so raw emails,
attachments, and OCR text have somewhere durable to live without coupling any
package to S3 — swapping in an S3-backed implementation later touches only
this file.
"""
from __future__ import annotations

import os
import uuid
from pathlib import Path
from typing import Protocol


class BlobStorage(Protocol):
    def put(self, data: bytes, *, suffix: str = "") -> str:
        """Persist `data`, returning an opaque reference usable with `get`."""
        ...

    def get(self, ref: str) -> bytes:
        """Retrieve previously stored bytes by reference."""
        ...


class LocalFileStorage:
    def __init__(self, root: str | os.PathLike | None = None) -> None:
        self.root = Path(root or os.environ.get("STORAGE_ROOT", ".data/storage"))
        self.root.mkdir(parents=True, exist_ok=True)

    def put(self, data: bytes, *, suffix: str = "") -> str:
        key = f"{uuid.uuid4().hex}{suffix}"
        (self.root / key).write_bytes(data)
        return key

    def get(self, ref: str) -> bytes:
        return (self.root / ref).read_bytes()
