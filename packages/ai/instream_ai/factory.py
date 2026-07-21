from __future__ import annotations

import os

from instream_shared.errors import ConfigError

from instream_ai.base import AIProvider
from instream_ai.mock import MockAIProvider
from instream_ai.stubs import AnthropicProvider, OpenAIProvider

_PROVIDERS = {
    "mock": MockAIProvider,
    "anthropic": AnthropicProvider,
    "openai": OpenAIProvider,
}


def get_ai_provider(name: str | None = None) -> AIProvider:
    name = name or os.environ.get("AI_PROVIDER", "mock")
    provider_cls = _PROVIDERS.get(name)
    if provider_cls is None:
        raise ConfigError(f"Unknown AI_PROVIDER: {name!r}")
    return provider_cls()
