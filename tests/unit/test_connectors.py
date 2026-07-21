from datetime import datetime, timezone

from instream_connectors import IMAPConnector, MockEmailConnector
from instream_shared.types import EmailAttachmentRef, EmailMessage


def test_mock_connector_returns_each_message_once():
    message = EmailMessage(
        message_id="<1@example.com>",
        sender="a@example.com",
        subject="Hi",
        body="hello",
        received_at=datetime.now(timezone.utc),
    )
    connector = MockEmailConnector([message])
    assert connector.fetch_new_messages() == [message]
    assert connector.fetch_new_messages() == []
    connector.mark_processed(message.message_id)
    assert connector.test_connection() is True


def test_imap_parses_plain_text_message():
    raw = (
        b"From: sender@example.com\r\n"
        b"Subject: Test Subject\r\n"
        b"Message-ID: <abc@example.com>\r\n"
        b"Content-Type: text/plain; charset=utf-8\r\n\r\n"
        b"Hello world"
    )
    parsed = IMAPConnector._parse(raw)
    assert parsed.sender == "sender@example.com"
    assert parsed.subject == "Test Subject"
    assert parsed.body.strip() == "Hello world"
    assert parsed.attachments == []


def test_email_attachment_ref_is_frozen():
    ref = EmailAttachmentRef(filename="a.pdf", mime_type="application/pdf", content=b"x")
    assert ref.filename == "a.pdf"
