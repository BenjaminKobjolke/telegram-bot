"""Pytest fixtures for telegram-bot tests."""

import pytest

from telegram_bot import Settings, TelegramBot


@pytest.fixture
def mock_settings() -> Settings:
    """Create mock settings for testing."""
    return Settings(
        bot_token="test_token_123",
        channel_id="@test_channel",
        base_url="https://example.com",
        parse_mode="HTML",
        poll_timeout=30,
        retry_delay=5.0,
        send_delay=0.1,
    )


@pytest.fixture
def reset_bot() -> None:
    """Reset the TelegramBot singleton before and after each test."""
    TelegramBot.reset_instance()
    yield
    TelegramBot.reset_instance()
