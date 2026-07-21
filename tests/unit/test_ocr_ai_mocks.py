import pytest
from instream_ai import MockAIProvider, get_ai_provider
from instream_ocr import MockOCRProvider, get_ocr_provider
from instream_shared.errors import UnsupportedProviderError


def test_mock_ocr_is_deterministic():
    provider = MockOCRProvider()
    a = provider.extract_text(b"bytes", filename="x.png")
    b = provider.extract_text(b"bytes", filename="x.png")
    assert a == b
    assert a.provider == "mock"


def test_mock_ai_classifies_by_keyword():
    provider = MockAIProvider()
    result = provider.classify_document("This is a Bank Statement for account 123")
    assert result.doc_type == "bank_statement"
    assert result.confidence > 0.5


def test_mock_ai_unknown_doc_type_low_confidence():
    provider = MockAIProvider()
    result = provider.classify_document("some random unrelated text")
    assert result.doc_type == "unknown"


def test_get_ocr_provider_factory_default_mock():
    provider = get_ocr_provider()
    assert isinstance(provider, MockOCRProvider)


def test_get_ai_provider_factory_unimplemented_raises():
    provider = get_ai_provider("anthropic")
    with pytest.raises(UnsupportedProviderError):
        provider.summarize("text")
