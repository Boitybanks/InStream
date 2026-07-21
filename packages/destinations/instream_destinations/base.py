from __future__ import annotations

from typing import Protocol


class DestinationConnector(Protocol):
    def write(self, record: dict) -> None: ...

    def test_connection(self) -> bool: ...
