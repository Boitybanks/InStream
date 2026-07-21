from __future__ import annotations

from instream_shared.errors import ConfigError

from instream_connectors.base import EmailConnector
from instream_connectors.imap_connector import IMAPConfig, IMAPConnector
from instream_connectors.stubs import ExchangeConnector, GmailConnector, OutlookConnector

_STUBS = {
    "outlook": OutlookConnector,
    "gmail": GmailConnector,
    "exchange": ExchangeConnector,
}


def get_connector(connector_type: str, config: dict) -> EmailConnector:
    if connector_type == "imap":
        return IMAPConnector(IMAPConfig(**config))
    stub_cls = _STUBS.get(connector_type)
    if stub_cls is not None:
        return stub_cls()
    raise ConfigError(f"Unknown connector_type: {connector_type!r}")
