from __future__ import annotations

import email
import imaplib
from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

from instream_shared.errors import ConnectorError
from instream_shared.types import EmailAttachmentRef, EmailMessage


@dataclass(frozen=True)
class IMAPConfig:
    host: str
    username: str
    password: str
    port: int = 993
    mailbox: str = "INBOX"
    use_ssl: bool = True


class IMAPConnector:
    """Reference EmailConnector implementation — works against any standard
    IMAP mailbox. Outlook/Gmail/Exchange get their own connectors later
    (OAuth flows, vendor APIs) but all satisfy the same `EmailConnector`
    protocol.
    """

    def __init__(self, config: IMAPConfig) -> None:
        self._config = config

    def _connect(self) -> imaplib.IMAP4:
        client_cls = imaplib.IMAP4_SSL if self._config.use_ssl else imaplib.IMAP4
        try:
            conn = client_cls(self._config.host, self._config.port)
            conn.login(self._config.username, self._config.password)
            conn.select(self._config.mailbox)
        except (imaplib.IMAP4.error, OSError) as exc:
            raise ConnectorError(f"IMAP connection failed: {exc}") from exc
        return conn

    def fetch_new_messages(self) -> list[EmailMessage]:
        conn = self._connect()
        try:
            status, data = conn.search(None, "UNSEEN")
            if status != "OK":
                raise ConnectorError(f"IMAP search failed with status {status}")
            messages: list[EmailMessage] = []
            for message_num in data[0].split():
                fetch_status, msg_data = conn.fetch(message_num, "(RFC822)")
                if fetch_status != "OK" or not msg_data or msg_data[0] is None:
                    continue
                raw = msg_data[0][1]
                messages.append(self._parse(raw))
            return messages
        finally:
            conn.logout()

    def mark_processed(self, message_id: str) -> None:
        conn = self._connect()
        try:
            status, data = conn.search(None, "HEADER", "Message-ID", message_id)
            if status == "OK":
                for message_num in data[0].split():
                    conn.store(message_num, "+FLAGS", "\\Seen")
        finally:
            conn.logout()

    def send_reply(self, message_id: str, body: str) -> None:
        raise NotImplementedError(
            "Sending replies requires an SMTP connector — not wired up in Phase 1"
        )

    def test_connection(self) -> bool:
        conn = self._connect()
        conn.logout()
        return True

    @staticmethod
    def _parse(raw: bytes) -> EmailMessage:
        msg = email.message_from_bytes(raw)
        attachments: list[EmailAttachmentRef] = []
        body_text = ""

        if msg.is_multipart():
            for part in msg.walk():
                disposition = str(part.get("Content-Disposition") or "")
                if "attachment" in disposition:
                    payload = part.get_payload(decode=True) or b""
                    attachments.append(
                        EmailAttachmentRef(
                            filename=part.get_filename() or "attachment",
                            mime_type=part.get_content_type(),
                            content=payload,
                        )
                    )
                elif part.get_content_type() == "text/plain" and not body_text:
                    payload = part.get_payload(decode=True) or b""
                    charset = part.get_content_charset() or "utf-8"
                    body_text = payload.decode(charset, errors="replace")
        else:
            payload = msg.get_payload(decode=True) or b""
            charset = msg.get_content_charset() or "utf-8"
            body_text = payload.decode(charset, errors="replace")

        received_at = datetime.now(timezone.utc)
        date_header = msg.get("Date")
        if date_header:
            try:
                received_at = parsedate_to_datetime(date_header)
            except (TypeError, ValueError):
                pass

        return EmailMessage(
            message_id=msg.get("Message-ID", ""),
            sender=msg.get("From", ""),
            subject=msg.get("Subject", ""),
            body=body_text,
            received_at=received_at,
            attachments=attachments,
        )
