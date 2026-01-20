"""Tests for handlers module."""

from unittest.mock import MagicMock

from telegram_bot import HandlerRegistry


class TestHandlerRegistry:
    """Tests for the HandlerRegistry class."""

    def test_registry_add_handler(self) -> None:
        """Test adding a handler to the registry."""
        registry = HandlerRegistry()
        handler = MagicMock()

        registry.add(handler)

        assert len(registry) == 1
        assert handler in registry.handlers

    def test_registry_add_duplicate_handler(self) -> None:
        """Test that duplicate handlers are not added."""
        registry = HandlerRegistry()
        handler = MagicMock()

        registry.add(handler)
        registry.add(handler)

        assert len(registry) == 1

    def test_registry_remove_handler(self) -> None:
        """Test removing a handler from the registry."""
        registry = HandlerRegistry()
        handler = MagicMock()

        registry.add(handler)
        result = registry.remove(handler)

        assert result is True
        assert len(registry) == 0

    def test_registry_remove_nonexistent_handler(self) -> None:
        """Test removing a handler that doesn't exist."""
        registry = HandlerRegistry()
        handler = MagicMock()

        result = registry.remove(handler)

        assert result is False

    def test_registry_clear(self) -> None:
        """Test clearing all handlers."""
        registry = HandlerRegistry()
        registry.add(MagicMock())
        registry.add(MagicMock())

        registry.clear()

        assert len(registry) == 0

    def test_registry_handlers_returns_copy(self) -> None:
        """Test that handlers property returns a copy."""
        registry = HandlerRegistry()
        handler = MagicMock()
        registry.add(handler)

        handlers = registry.handlers
        handlers.clear()  # Modify the copy

        assert len(registry) == 1  # Original unchanged

    def test_registry_bool_empty(self) -> None:
        """Test bool returns False for empty registry."""
        registry = HandlerRegistry()
        assert not registry

    def test_registry_bool_with_handlers(self) -> None:
        """Test bool returns True with handlers."""
        registry = HandlerRegistry()
        registry.add(MagicMock())
        assert registry
