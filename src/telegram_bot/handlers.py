"""Message handler management for the Telegram bot library."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from telegram import Update


class MessageHandler(Protocol):
    """Protocol for message handler functions."""

    def __call__(self, update: Update) -> None:
        """
        Handle an incoming Telegram update.

        Args:
            update: The Telegram update object containing the message.
        """
        ...


@dataclass
class HandlerRegistry:
    """Registry for managing message handlers."""

    _handlers: list[MessageHandler] = field(default_factory=list)

    def add(self, handler: MessageHandler) -> None:
        """
        Add a message handler to the registry.

        Args:
            handler: A callable that accepts a telegram.Update object.
        """
        if handler not in self._handlers:
            self._handlers.append(handler)

    def remove(self, handler: MessageHandler) -> bool:
        """
        Remove a message handler from the registry.

        Args:
            handler: The handler to remove.

        Returns:
            True if the handler was removed, False if it wasn't found.
        """
        if handler in self._handlers:
            self._handlers.remove(handler)
            return True
        return False

    def clear(self) -> None:
        """Remove all handlers from the registry."""
        self._handlers.clear()

    @property
    def handlers(self) -> list[MessageHandler]:
        """Return a copy of the handlers list."""
        return list(self._handlers)

    def __len__(self) -> int:
        """Return the number of registered handlers."""
        return len(self._handlers)

    def __bool__(self) -> bool:
        """Return True if there are any registered handlers."""
        return len(self._handlers) > 0
