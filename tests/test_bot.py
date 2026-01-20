"""Tests for the TelegramBot class."""

from unittest.mock import MagicMock, patch

import pytest

from telegram_bot import NotInitializedError, Settings, TelegramBot


class TestTelegramBotSingleton:
    """Tests for singleton pattern."""

    def test_singleton_same_instance(self, reset_bot: None) -> None:
        """Test that get_instance returns the same instance."""
        bot1 = TelegramBot.get_instance()
        bot2 = TelegramBot.get_instance()

        assert bot1 is bot2

    def test_singleton_new_same_instance(self, reset_bot: None) -> None:
        """Test that direct instantiation returns same instance."""
        bot1 = TelegramBot()
        bot2 = TelegramBot()

        assert bot1 is bot2

    def test_reset_instance(self, reset_bot: None) -> None:
        """Test that reset_instance creates a fresh state."""
        _bot1 = TelegramBot.get_instance()
        TelegramBot.reset_instance()
        _bot2 = TelegramBot.get_instance()

        # After reset, should be a new instance
        assert TelegramBot._initialized is False


class TestTelegramBotInitialization:
    """Tests for bot initialization."""

    def test_initialize_with_settings(
        self, reset_bot: None, mock_settings: Settings
    ) -> None:
        """Test initialization with explicit settings."""
        with patch("telegram_bot.bot.telegram.Bot"):
            bot = TelegramBot.get_instance()
            bot.initialize(settings=mock_settings)

            assert TelegramBot._initialized is True
            assert TelegramBot._settings == mock_settings

    def test_initialize_only_once(
        self, reset_bot: None, mock_settings: Settings
    ) -> None:
        """Test that initialize only runs once."""
        with patch("telegram_bot.bot.telegram.Bot") as mock_bot_class:
            bot = TelegramBot.get_instance()
            bot.initialize(settings=mock_settings)
            bot.initialize(settings=mock_settings)

            # Bot should only be created once
            assert mock_bot_class.call_count == 1

    def test_not_initialized_error(self, reset_bot: None) -> None:
        """Test that methods raise error when not initialized."""
        bot = TelegramBot.get_instance()

        with pytest.raises(NotInitializedError):
            bot.send_message_sync("test")


class TestTelegramBotMessaging:
    """Tests for message sending."""

    def test_send_message_sync_queues_message(
        self, reset_bot: None, mock_settings: Settings
    ) -> None:
        """Test that send_message_sync adds message to queue."""
        with patch("telegram_bot.bot.telegram.Bot"):
            bot = TelegramBot.get_instance()
            bot.initialize(settings=mock_settings)

            # Add a dummy handler to avoid warning
            bot.add_message_handler(MagicMock())

            # Clear the queue before test
            while not TelegramBot._channel_queue.empty():
                TelegramBot._channel_queue.get_nowait()

            bot.send_message_sync("test message")

            assert not TelegramBot._channel_queue.empty()
            msg = TelegramBot._channel_queue.get_nowait()
            assert msg == "test message"

    def test_reply_to_user_queues_message(
        self, reset_bot: None, mock_settings: Settings
    ) -> None:
        """Test that reply_to_user adds message to direct queue."""
        with patch("telegram_bot.bot.telegram.Bot"):
            bot = TelegramBot.get_instance()
            bot.initialize(settings=mock_settings)

            bot.add_message_handler(MagicMock())

            while not TelegramBot._direct_queue.empty():
                TelegramBot._direct_queue.get_nowait()

            bot.reply_to_user("direct message", chat_id=12345)

            assert not TelegramBot._direct_queue.empty()
            msg, chat_id = TelegramBot._direct_queue.get_nowait()
            assert msg == "direct message"
            assert chat_id == 12345

    def test_send_url_sync_constructs_url(
        self, reset_bot: None, mock_settings: Settings
    ) -> None:
        """Test that send_url_sync constructs full URL."""
        with patch("telegram_bot.bot.telegram.Bot"):
            bot = TelegramBot.get_instance()
            bot.initialize(settings=mock_settings)

            bot.add_message_handler(MagicMock())

            while not TelegramBot._channel_queue.empty():
                TelegramBot._channel_queue.get_nowait()

            bot.send_url_sync("/test/path")

            msg = TelegramBot._channel_queue.get_nowait()
            assert msg == "https://example.com/test/path"


class TestTelegramBotHandlers:
    """Tests for message handler management."""

    def test_add_message_handler(
        self, reset_bot: None, mock_settings: Settings
    ) -> None:
        """Test adding a message handler."""
        with patch("telegram_bot.bot.telegram.Bot"):
            bot = TelegramBot.get_instance()
            bot.initialize(settings=mock_settings)

            handler = MagicMock()
            bot.add_message_handler(handler)

            assert len(TelegramBot._handler_registry) == 1

    def test_remove_message_handler(
        self, reset_bot: None, mock_settings: Settings
    ) -> None:
        """Test removing a message handler."""
        with patch("telegram_bot.bot.telegram.Bot"):
            bot = TelegramBot.get_instance()
            bot.initialize(settings=mock_settings)

            handler = MagicMock()
            bot.add_message_handler(handler)
            result = bot.remove_message_handler(handler)

            assert result is True
            assert len(TelegramBot._handler_registry) == 0

    def test_clear_handlers(
        self, reset_bot: None, mock_settings: Settings
    ) -> None:
        """Test clearing all handlers."""
        with patch("telegram_bot.bot.telegram.Bot"):
            bot = TelegramBot.get_instance()
            bot.initialize(settings=mock_settings)

            bot.add_message_handler(MagicMock())
            bot.add_message_handler(MagicMock())
            bot.clear_handlers()

            assert len(TelegramBot._handler_registry) == 0
