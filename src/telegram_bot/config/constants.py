"""Constants for the Telegram bot library."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Constants:
    """Immutable constants for the Telegram bot library."""

    # Environment variable names
    ENV_BOT_TOKEN: str = "TELEGRAM_BOT_TOKEN"
    ENV_CHANNEL_ID: str = "TELEGRAM_CHANNEL_ID"
    ENV_BASE_URL: str = "TELEGRAM_BASE_URL"
    ENV_PARSE_MODE: str = "TELEGRAM_PARSE_MODE"
    ENV_POLL_TIMEOUT: str = "TELEGRAM_POLL_TIMEOUT"
    ENV_RETRY_DELAY: str = "TELEGRAM_RETRY_DELAY"
    ENV_SEND_DELAY: str = "TELEGRAM_SEND_DELAY"

    # Default values
    DEFAULT_PARSE_MODE: str = "HTML"
    DEFAULT_POLL_TIMEOUT: int = 30
    DEFAULT_RETRY_DELAY: float = 5.0
    DEFAULT_SEND_DELAY: float = 0.1
    DEFAULT_BASE_URL: str = ""

    # Log messages
    LOG_STARTED_RECEIVING: str = "Started receiving messages"
    LOG_STOPPED_RECEIVING: str = "Stopped receiving messages"
    LOG_NO_HANDLERS_WARNING: str = (
        "Warning: No message handlers registered. Use add_message_handler() to receive messages."
    )
    LOG_NO_HANDLERS_START: str = (
        "Warning: No message handlers registered. Use add_message_handler() first."
    )

    # Error messages
    ERR_NOT_INITIALIZED: str = "TelegramBot is not initialized. Call initialize() first."
    ERR_MISSING_BOT_TOKEN: str = "Bot token is required"
    ERR_MISSING_CHANNEL_ID: str = "Channel ID is required"
    ERR_HANDLER_FAILED: str = "Error in message handler: {error}"
    ERR_POLLING_FAILED: str = "Error polling updates: {error}"
    ERR_SEND_FAILED: str = "Error sending message: {error}"
    ERR_WORKER_FAILED: str = "Worker thread error: {error}"
    ERR_INVALID_SETTINGS: str = "Invalid settings: {error}"


# Global singleton instance
CONSTANTS = Constants()
