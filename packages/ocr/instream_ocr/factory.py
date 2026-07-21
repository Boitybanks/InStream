from __future__ import annotations

import os

from instream_shared.errors import ConfigError

from instream_ocr.base import OCRProvider
from instream_ocr.mock import MockOCRProvider
from instream_ocr.stubs import AWSTextractProvider, AzureDocumentIntelligenceProvider, GoogleVisionProvider

_PROVIDERS = {
    "mock": MockOCRProvider,
    "azure_document_intelligence": AzureDocumentIntelligenceProvider,
    "aws_textract": AWSTextractProvider,
    "google_vision": GoogleVisionProvider,
}


def get_ocr_provider(name: str | None = None) -> OCRProvider:
    name = name or os.environ.get("OCR_PROVIDER", "mock")
    provider_cls = _PROVIDERS.get(name)
    if provider_cls is None:
        raise ConfigError(f"Unknown OCR_PROVIDER: {name!r}")
    return provider_cls()
