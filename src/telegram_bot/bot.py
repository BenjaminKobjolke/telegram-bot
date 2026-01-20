"""Core Telegram bot implementation with singleton pattern."""

from __future__ import annotations

import asyncio
import logging
import threading
import time
from collections.abc import Callable
from functools import wraps
from pathlib import Path
from queue import Queue
from typing import TYPE_CHECKING, Any, TypeVar

import telegram

from .config import CONSTANTS, Settings, get_settings
from .exceptions import NotInitializedError
from .handlers import HandlerRegistry, MessageHandler

if TYPE_CHECKING:
    from telegram import Update

# Disable httpx logging
logging.getLogger("httpx").setLevel(logging.WARNING)

F = TypeVar("F", bound=Callable[..., Any])


def requires_initialization(func: F) -> F:
    """Decorator to ensure bot is initialized before method execution."""

    @wraps(func)
    def wrapper(self: TelegramBot, *args: Any, **kwargs: Any) -> Any:
        if not TelegramBot._initialized:
            raise NotInitializedError(CONSTANTS.ERR_NOT_INITIALIZED)
        return func(self, *args, **kwargs)

    return wrapper  # type: ignore[return-value]


def warns_no_handlers(func: F) -> F:
    """Decorator to warn if no message handlers are registered."""

    @wraps(func)
    def wrapper(self: TelegramBot, *args: Any, **kwargs: Any) -> Any:
        if not TelegramBot._handler_registry:
            print(CONSTANTS.LOG_NO_HANDLERS_WARNING)
        return func(self, *args, **kwargs)

    return wrapper  # type: ignore[return-value]


class TelegramBot:
    """
    Singleton Telegram bot with async message handling.

    This class implements a thread-safe singleton pattern for managing
    Telegram bot communications. It supports both channel messages and
    direct messages through separate queues.

    Usage:
        bot = TelegramBot.get_instance()
        bot.initialize()  # Uses .env file
        bot.add_message_handler(my_handler)
        bot.send_message_sync("Hello!")
        bot.shutdown()
    """

    _instance: TelegramBot | None = None
    _initialized: bool = False
    _bot: telegram.Bot | None = None
    _settings: Settings | None = None
    _channel_queue: Queue[str] = Queue()
    _direct_queue: Queue[tuple[str, int]] = Queue()
    _worker_thread: threading.Thread | None = None
    _polling_thread: threading.Thread | None = None
    _stop_flag: bool = False
    _is_polling: bool = False
    _loop: asyncio.AbstractEventLoop | None = None
    _handler_registry: HandlerRegistry = HandlerRegistry()
    _lock: threading.Lock = threading.Lock()

    def __new__(cls) -> TelegramBot:
        """Ensure only one instance exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def get_instance(cls) -> TelegramBot:
        """
        Get or create the TelegramBot singleton instance.

        Returns:
            The singleton TelegramBot instance.
        """
        if cls._instance is None:
            cls._instance = TelegramBot()
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """
        Reset the singleton instance. Useful for testing.

        This will shutdown the existing instance if it's running.
        """
        with cls._lock:
            if cls._instance is not None:
                try:
                    cls._instance.shutdown()
                except Exception:
                    pass
            cls._instance = None
            cls._initialized = False
            cls._bot = None
            cls._settings = None
            cls._channel_queue = Queue()
            cls._direct_queue = Queue()
            cls._worker_thread = None
            cls._polling_thread = None
            cls._stop_flag = False
            cls._is_polling = False
            cls._loop = None
            cls._handler_registry = HandlerRegistry()

    def initialize(
        self,
        settings: Settings | None = None,
        env_path: str | Path | None = None,
    ) -> None:
        """
        Initialize the Telegram bot.

        Args:
            settings: Optional Settings object. If not provided, loads from env.
            env_path: Optional path to .env file for loading settings.

        Raises:
            ValueError: If required settings are missing.
        """
        if TelegramBot._initialized:
            return

        with TelegramBot._lock:
            if TelegramBot._initialized:
                return

            if settings is not None:
                TelegramBot._settings = settings
            else:
                TelegramBot._settings = get_settings(env_path)

            TelegramBot._bot = telegram.Bot(token=TelegramBot._settings.bot_token)
            TelegramBot._stop_flag = False

            # Start worker thread
            if TelegramBot._worker_thread is None or not TelegramBot._worker_thread.is_alive():
                TelegramBot._worker_thread = threading.Thread(
                    target=self._message_worker, daemon=True
                )
                TelegramBot._worker_thread.start()

            TelegramBot._initialized = True

    def add_message_handler(self, handler: MessageHandler) -> None:
        """
        Add a message handler function.

        The handler will be called for each incoming message update.
        Adding the first handler automatically starts receiving messages.

        Args:
            handler: A callable that accepts a telegram.Update object.
        """
        TelegramBot._handler_registry.add(handler)
        if len(TelegramBot._handler_registry) == 1:
            self.start_receiving()

    def remove_message_handler(self, handler: MessageHandler) -> bool:
        """
        Remove a message handler.

        Args:
            handler: The handler to remove.

        Returns:
            True if the handler was removed, False if it wasn't found.
        """
        return TelegramBot._handler_registry.remove(handler)

    def clear_handlers(self) -> None:
        """Remove all message handlers."""
        TelegramBot._handler_registry.clear()

    @requires_initialization
    def start_receiving(self) -> None:
        """
        Start receiving messages from Telegram.

        This must be called after adding message handlers if you want
        to receive incoming messages.
        """
        if not TelegramBot._handler_registry:
            print(CONSTANTS.LOG_NO_HANDLERS_START)
            return

        if not TelegramBot._is_polling:
            TelegramBot._is_polling = True
            if TelegramBot._polling_thread is None or not TelegramBot._polling_thread.is_alive():
                TelegramBot._polling_thread = threading.Thread(
                    target=self._start_polling, daemon=True
                )
                TelegramBot._polling_thread.start()
                print(CONSTANTS.LOG_STARTED_RECEIVING)

    def stop_receiving(self) -> None:
        """Stop receiving messages from Telegram."""
        TelegramBot._is_polling = False
        if TelegramBot._polling_thread is not None and TelegramBot._polling_thread.is_alive():
            TelegramBot._polling_thread.join(timeout=5.0)
        print(CONSTANTS.LOG_STOPPED_RECEIVING)

    @requires_initialization
    @warns_no_handlers
    def send_message_sync(self, message: str) -> None:
        """
        Send a message to the configured channel.

        This method is synchronous but uses a background worker thread
        to actually send the message.

        Args:
            message: The message text to send.
        """
        TelegramBot._channel_queue.put(message)

    @requires_initialization
    @warns_no_handlers
    def reply_to_user(self, message: str, chat_id: int) -> None:
        """
        Send a direct message to a specific user.

        Args:
            message: The message text to send.
            chat_id: The chat ID of the user to send to.
        """
        TelegramBot._direct_queue.put((message, chat_id))

    @requires_initialization
    @warns_no_handlers
    def send_url_sync(self, path: str) -> None:
        """
        Send a URL with the configured base URL prefix.

        Args:
            path: The path to append to the base URL.
        """
        if TelegramBot._settings is None:
            raise NotInitializedError(CONSTANTS.ERR_NOT_INITIALIZED)

        base = TelegramBot._settings.base_url.rstrip("/")
        path_clean = path.lstrip("/")
        full_url = f"{base}/{path_clean}" if base else path_clean
        TelegramBot._channel_queue.put(full_url)

    def shutdown(self) -> None:
        """Shutdown the bot and cleanup resources."""
        TelegramBot._stop_flag = True
        self.stop_receiving()

        if TelegramBot._worker_thread is not None and TelegramBot._worker_thread.is_alive():
            TelegramBot._worker_thread.join(timeout=5.0)

        if TelegramBot._loop is not None:
            if TelegramBot._loop.is_running():
                TelegramBot._loop.stop()
            if not TelegramBot._loop.is_closed():
                TelegramBot._loop.close()

        TelegramBot._initialized = False

    # Private methods

    async def _send_message(self, message: str, chat_id: int | str | None = None) -> None:
        """Send a message asynchronously."""
        if TelegramBot._bot is None or TelegramBot._settings is None:
            return

        try:
            target = chat_id if chat_id is not None else TelegramBot._settings.normalized_channel_id
            await TelegramBot._bot.send_message(
                chat_id=target,
                text=message,
                parse_mode=TelegramBot._settings.parse_mode,
            )
        except Exception as e:
            print(CONSTANTS.ERR_SEND_FAILED.format(error=str(e)))

    def _message_worker(self) -> None:
        """Background worker that processes messages from the queues."""
        TelegramBot._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(TelegramBot._loop)

        while not TelegramBot._stop_flag:
            try:
                # Process direct messages first (higher priority)
                try:
                    message, chat_id = TelegramBot._direct_queue.get_nowait()
                    TelegramBot._loop.run_until_complete(self._send_message(message, chat_id))
                except Exception:
                    # No direct messages, try channel messages
                    try:
                        message = TelegramBot._channel_queue.get(timeout=1.0)
                        TelegramBot._loop.run_until_complete(self._send_message(message))
                    except Exception:
                        continue

                # Small delay to prevent too rapid sending
                if TelegramBot._settings:
                    time.sleep(TelegramBot._settings.send_delay)

            except Exception as e:
                print(CONSTANTS.ERR_WORKER_FAILED.format(error=str(e)))

        # Cleanup event loop
        if TelegramBot._loop is not None:
            if TelegramBot._loop.is_running():
                TelegramBot._loop.stop()
            if not TelegramBot._loop.is_closed():
                TelegramBot._loop.close()

    async def _handle_update(self, update: Update) -> None:
        """Handle an incoming update from Telegram."""
        if update.message:
            # Filter by allowed user IDs
            if TelegramBot._settings and TelegramBot._settings.allowed_user_ids:
                user = update.message.from_user
                if user and user.id not in TelegramBot._settings.allowed_user_ids:
                    return  # Silently ignore unauthorized users

            for handler in TelegramBot._handler_registry.handlers:
                try:
                    handler(update)
                except Exception as e:
                    print(CONSTANTS.ERR_HANDLER_FAILED.format(error=str(e)))

    async def _poll_updates(self) -> None:
        """Continuously poll for updates from Telegram."""
        if TelegramBot._bot is None or TelegramBot._settings is None:
            return

        offset: int | None = None
        while not TelegramBot._stop_flag and TelegramBot._is_polling:
            try:
                updates = await TelegramBot._bot.get_updates(
                    offset=offset, timeout=TelegramBot._settings.poll_timeout
                )
                for update in updates:
                    await self._handle_update(update)
                    offset = update.update_id + 1
            except Exception as e:
                print(CONSTANTS.ERR_POLLING_FAILED.format(error=str(e)))
                await asyncio.sleep(TelegramBot._settings.retry_delay)

    def _start_polling(self) -> None:
        """Start the polling loop in a background thread."""
        polling_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(polling_loop)
        polling_loop.run_until_complete(self._poll_updates())
