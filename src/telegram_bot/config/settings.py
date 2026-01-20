"""Settings management for the Telegram bot library."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from dotenv import load_dotenv

from .constants import CONSTANTS

if TYPE_CHECKING:
    pass


@dataclass(frozen=True)
class Settings:
    """Immutable settings for the Telegram bot."""

    bot_token: str
    channel_id: str
    base_url: str = CONSTANTS.DEFAULT_BASE_URL
    parse_mode: str = CONSTANTS.DEFAULT_PARSE_MODE
    poll_timeout: int = CONSTANTS.DEFAULT_POLL_TIMEOUT
    retry_delay: float = CONSTANTS.DEFAULT_RETRY_DELAY
    send_delay: float = CONSTANTS.DEFAULT_SEND_DELAY

    def __post_init__(self) -> None:
        """Validate settings after initialization."""
        if not self.bot_token:
            raise ValueError(CONSTANTS.ERR_MISSING_BOT_TOKEN)
        if not self.channel_id:
            raise ValueError(CONSTANTS.ERR_MISSING_CHANNEL_ID)

    @property
    def normalized_channel_id(self) -> str:
        """Return channel ID with @ prefix if needed."""
        if self.channel_id.startswith("@") or self.channel_id.startswith("-100"):
            return self.channel_id
        return f"@{self.channel_id}"


def get_settings(env_path: str | Path | None = None) -> Settings:
    """
    Load settings from environment variables.

    Args:
        env_path: Optional path to .env file. If None, uses default .env loading.

    Returns:
        Settings object with values from environment.

    Raises:
        ValueError: If required settings are missing.
    """
    if env_path is not None:
        load_dotenv(env_path)
    else:
        load_dotenv()

    bot_token = os.getenv(CONSTANTS.ENV_BOT_TOKEN, "")
    channel_id = os.getenv(CONSTANTS.ENV_CHANNEL_ID, "")
    base_url = os.getenv(CONSTANTS.ENV_BASE_URL, CONSTANTS.DEFAULT_BASE_URL)
    parse_mode = os.getenv(CONSTANTS.ENV_PARSE_MODE, CONSTANTS.DEFAULT_PARSE_MODE)

    poll_timeout_str = os.getenv(CONSTANTS.ENV_POLL_TIMEOUT, "")
    poll_timeout = (
        int(poll_timeout_str) if poll_timeout_str else CONSTANTS.DEFAULT_POLL_TIMEOUT
    )

    retry_delay_str = os.getenv(CONSTANTS.ENV_RETRY_DELAY, "")
    retry_delay = (
        float(retry_delay_str) if retry_delay_str else CONSTANTS.DEFAULT_RETRY_DELAY
    )

    send_delay_str = os.getenv(CONSTANTS.ENV_SEND_DELAY, "")
    send_delay = (
        float(send_delay_str) if send_delay_str else CONSTANTS.DEFAULT_SEND_DELAY
    )

    return Settings(
        bot_token=bot_token,
        channel_id=channel_id,
        base_url=base_url,
        parse_mode=parse_mode,
        poll_timeout=poll_timeout,
        retry_delay=retry_delay,
        send_delay=send_delay,
    )
