from __future__ import annotations

from instream_shared.types import EmailMessage


class MockEmailConnector:
    """Deterministic connector for tests and for exercising the worker
    pipeline end-to-end without a live mailbox. `fetch_new_messages` returns
    each seeded message exactly once."""

    def __init__(self, messages: list[EmailMessage] | None = None) -> None:
        self._pending = list(messages or [])
        self._processed: list[str] = []
        self.sent_replies: list[tuple[str, str]] = []

    def fetch_new_messages(self) -> list[EmailMessage]:
        messages, self._pending = self._pending, []
        return messages

    def mark_processed(self, message_id: str) -> None:
        self._processed.append(message_id)

    def send_reply(self, message_id: str, body: str) -> None:
        self.sent_replies.append((message_id, body))

    def test_connection(self) -> bool:
        return True
