from __future__ import annotations

from instream_shared.errors import UnsupportedProviderError
from instream_shared.types import EmailMessage


class _UnimplementedConnector:
    """Placeholder satisfying the EmailConnector protocol so the platform's
    connector registry, config schema, and UI dropdowns can reference these
    providers today. Wiring the real OAuth/API integration is Phase 4."""

    provider_name = "unimplemented"

    def fetch_new_messages(self) -> list[EmailMessage]:
        raise UnsupportedProviderError(
            f"{self.provider_name} connector is not implemented yet (planned for Phase 4)"
        )

    def mark_processed(self, message_id: str) -> None:
        raise UnsupportedProviderError(f"{self.provider_name} connector is not implemented yet")

    def send_reply(self, message_id: str, body: str) -> None:
        raise UnsupportedProviderError(f"{self.provider_name} connector is not implemented yet")

    def test_connection(self) -> bool:
        raise UnsupportedProviderError(f"{self.provider_name} connector is not implemented yet")


class OutlookConnector(_UnimplementedConnector):
    provider_name = "outlook"


class GmailConnector(_UnimplementedConnector):
    provider_name = "gmail"


class ExchangeConnector(_UnimplementedConnector):
    provider_name = "exchange"
