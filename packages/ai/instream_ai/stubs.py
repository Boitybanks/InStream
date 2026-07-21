from __future__ import annotations

from instream_shared.errors import UnsupportedProviderError
from instream_shared.types import ClassificationResult, ExtractedField


class _UnimplementedAIProvider:
    provider_name = "unimplemented"

    def classify_document(self, text: str, *, candidate_types: list[str] | None = None) -> ClassificationResult:
        raise UnsupportedProviderError(f"AI provider {self.provider_name!r} needs an API key — see .env.example")

    def summarize(self, text: str) -> str:
        raise UnsupportedProviderError(f"AI provider {self.provider_name!r} needs an API key — see .env.example")

    def draft_email(self, context: dict) -> str:
        raise UnsupportedProviderError(f"AI provider {self.provider_name!r} needs an API key — see .env.example")

    def extract_fields(self, text: str, doc_type: str) -> dict[str, ExtractedField]:
        raise UnsupportedProviderError(f"AI provider {self.provider_name!r} needs an API key — see .env.example")


class AnthropicProvider(_UnimplementedAIProvider):
    provider_name = "anthropic"


class OpenAIProvider(_UnimplementedAIProvider):
    provider_name = "openai"
