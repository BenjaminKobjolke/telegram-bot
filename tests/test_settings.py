"""Tests for settings module."""

from pathlib import Path

import pytest

from telegram_bot import Settings, get_settings
from telegram_bot.config import CONSTANTS


class TestSettings:
    """Tests for the Settings dataclass."""

    def test_settings_creation(self) -> None:
        """Test creating settings with valid values."""
        settings = Settings(
            bot_token="test_token",
            channel_id="@test_channel",
        )
        assert settings.bot_token == "test_token"
        assert settings.channel_id == "@test_channel"

    def test_settings_immutable(self) -> None:
        """Test that settings are immutable (frozen)."""
        settings = Settings(
            bot_token="test_token",
            channel_id="@test_channel",
        )
        with pytest.raises(AttributeError):
            settings.bot_token = "new_token"  # type: ignore[misc]

    def test_settings_default_values(self) -> None:
        """Test default values are applied."""
        settings = Settings(
            bot_token="test_token",
            channel_id="@test_channel",
        )
        assert settings.base_url == CONSTANTS.DEFAULT_BASE_URL
        assert settings.parse_mode == CONSTANTS.DEFAULT_PARSE_MODE
        assert settings.poll_timeout == CONSTANTS.DEFAULT_POLL_TIMEOUT
        assert settings.retry_delay == CONSTANTS.DEFAULT_RETRY_DELAY
        assert settings.send_delay == CONSTANTS.DEFAULT_SEND_DELAY

    def test_settings_missing_bot_token(self) -> None:
        """Test that missing bot_token raises ValueError."""
        with pytest.raises(ValueError, match="Bot token is required"):
            Settings(bot_token="", channel_id="@test_channel")

    def test_settings_missing_channel_id(self) -> None:
        """Test that missing channel_id raises ValueError."""
        with pytest.raises(ValueError, match="Channel ID is required"):
            Settings(bot_token="test_token", channel_id="")

    def test_normalized_channel_id_with_at(self) -> None:
        """Test normalized_channel_id when already has @ prefix."""
        settings = Settings(bot_token="test_token", channel_id="@my_channel")
        assert settings.normalized_channel_id == "@my_channel"

    def test_normalized_channel_id_without_at(self) -> None:
        """Test normalized_channel_id adds @ prefix."""
        settings = Settings(bot_token="test_token", channel_id="my_channel")
        assert settings.normalized_channel_id == "@my_channel"

    def test_normalized_channel_id_numeric(self) -> None:
        """Test normalized_channel_id preserves numeric IDs."""
        settings = Settings(bot_token="test_token", channel_id="-100123456789")
        assert settings.normalized_channel_id == "-100123456789"


class TestGetSettings:
    """Tests for the get_settings function."""

    def test_get_settings_from_env_file(self, tmp_path: Path) -> None:
        """Test loading settings from an .env file."""
        env_file = tmp_path / ".env"
        env_file.write_text(
            "TELEGRAM_BOT_TOKEN=file_token\n"
            "TELEGRAM_CHANNEL_ID=@file_channel\n"
            "TELEGRAM_BASE_URL=https://file.example.com\n"
        )

        settings = get_settings(env_file)
        assert settings.bot_token == "file_token"
        assert settings.channel_id == "@file_channel"
        assert settings.base_url == "https://file.example.com"

    def test_get_settings_numeric_values(self, tmp_path: Path) -> None:
        """Test loading numeric settings from env file."""
        env_file = tmp_path / ".env"
        env_file.write_text(
            "TELEGRAM_BOT_TOKEN=test_token\n"
            "TELEGRAM_CHANNEL_ID=@test_channel\n"
            "TELEGRAM_POLL_TIMEOUT=60\n"
            "TELEGRAM_RETRY_DELAY=10.5\n"
            "TELEGRAM_SEND_DELAY=0.5\n"
        )

        settings = get_settings(env_file)
        assert settings.poll_timeout == 60
        assert settings.retry_delay == 10.5
        assert settings.send_delay == 0.5
