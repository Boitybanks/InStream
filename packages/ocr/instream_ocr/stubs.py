from __future__ import annotations

from instream_shared.errors import UnsupportedProviderError
from instream_shared.types import OCRResult


class _UnimplementedOCRProvider:
    provider_name = "unimplemented"

    def extract_text(self, image_bytes: bytes, *, filename: str = "") -> OCRResult:
        raise UnsupportedProviderError(
            f"OCR provider {self.provider_name!r} is not wired up yet — "
            "set OCR_PROVIDER=mock or supply the required credentials in a later phase."
        )


class AzureDocumentIntelligenceProvider(_UnimplementedOCRProvider):
    provider_name = "azure_document_intelligence"


class AWSTextractProvider(_UnimplementedOCRProvider):
    provider_name = "aws_textract"


class GoogleVisionProvider(_UnimplementedOCRProvider):
    provider_name = "google_vision"
