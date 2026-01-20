"""Telegram bot library with singleton pattern and async message handling."""

from .bot import TelegramBot
from .config import CONSTANTS, Constants, Settings, get_settings
from .exceptions import (
    ConfigurationError,
    HandlerError,
    NotInitializedError,
    TelegramBotError,
)
from .handlers import HandlerRegistry, MessageHandler

__all__ = [
    "TelegramBot",
    "Settings",
    "get_settings",
    "Constants",
    "CONSTANTS",
    "MessageHandler",
    "HandlerRegistry",
    "TelegramBotError",
    "ConfigurationError",
    "NotInitializedError",
    "HandlerError",
]

__version__ = "0.1.0"
