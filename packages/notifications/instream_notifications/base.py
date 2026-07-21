from __future__ import annotations

from typing import Protocol


class NotificationProvider(Protocol):
    def send(self, *, template: str, recipients: list[str], context: dict) -> None: ...
