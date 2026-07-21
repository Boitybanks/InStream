from __future__ import annotations

import logging

from jinja2 import Environment

logger = logging.getLogger("instream.notifications")
_env = Environment(autoescape=False)


class ConsoleNotificationProvider:
    """Renders the Jinja2 `template` string (usually loaded from a customer
    pack's `templates/` folder) and logs it instead of sending real email —
    a real SMTP/SES provider is a drop-in replacement behind the same
    interface."""

    def send(self, *, template: str, recipients: list[str], context: dict) -> None:
        rendered = _env.from_string(template).render(**context)
        logger.info("notification to=%s\n%s", ", ".join(recipients), rendered)
