"""Exceptions for the Telegram bot library."""


class TelegramBotError(Exception):
    """Base exception for all Telegram bot errors."""

    pass


class ConfigurationError(TelegramBotError):
    """Raised when there is a configuration error."""

    pass


class NotInitializedError(TelegramBotError):
    """Raised when the bot is used before initialization."""

    pass


class HandlerError(TelegramBotError):
    """Raised when there is an error in a message handler."""

    pass
