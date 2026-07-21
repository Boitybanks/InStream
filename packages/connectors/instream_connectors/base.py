from __future__ import annotations

from typing import Protocol

from instream_shared.types import EmailMessage


class EmailConnector(Protocol):
    """Every inbox integration implements this — nothing upstream should ever
    import `imaplib`, `msal`, or a Gmail SDK directly."""

    def fetch_new_messages(self) -> list[EmailMessage]: ...

    def mark_processed(self, message_id: str) -> None: ...

    def send_reply(self, message_id: str, body: str) -> None: ...

    def test_connection(self) -> bool: ...
