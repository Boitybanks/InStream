class InStreamError(Exception):
    """Base class for all platform errors."""


class NotFoundError(InStreamError):
    """Raised when a requested entity does not exist (or isn't visible to the tenant)."""


class ConfigError(InStreamError):
    """Raised when a rule/workflow/pack configuration is malformed."""


class ConnectorError(InStreamError):
    """Raised when an inbox or destination connector fails to communicate."""


class UnsupportedProviderError(InStreamError):
    """Raised when a configured OCR/AI provider has no implementation wired up yet."""
