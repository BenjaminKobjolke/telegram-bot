# Telegram Bot Library

A reusable Telegram bot library with singleton pattern, async message handling, and thread-safe operations.

## Features

- Singleton pattern for global bot access
- Async message handling with background worker threads
- Separate queues for channel and direct messages
- Polling-based update receiving
- Thread-safe operations
- Configurable via environment variables or explicit settings
- Type hints and immutable configuration

## Installation

### Development

```bash
# Clone the repository
git clone <repo-url>
cd telegram-bot

# Install with uv
uv sync

# Run tests
uv run pytest tests/ -v
```

### As a Dependency

Add to your project's `pyproject.toml`:

```toml
[project]
dependencies = [
    "telegram-bot",
]

[tool.uv.sources]
telegram-bot = { path = "D:\\GIT\\BenjaminKobjolke\\telegram-bot", editable = true }
```

Then run:
```bash
uv sync
```

## Configuration

Create a `.env` file in your project root:

```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHANNEL_ID=@your_channel
TELEGRAM_BASE_URL=https://your-server.com
TELEGRAM_PARSE_MODE=HTML
TELEGRAM_POLL_TIMEOUT=30
TELEGRAM_RETRY_DELAY=5.0
TELEGRAM_SEND_DELAY=0.1
```

Or configure programmatically:

```python
from telegram_bot import Settings

settings = Settings(
    bot_token="your_bot_token",
    channel_id="@your_channel",
    base_url="https://your-server.com",
)
```

## Usage

### Basic Usage

```python
from telegram_bot import TelegramBot

# Get the singleton instance
bot = TelegramBot.get_instance()

# Initialize (loads from .env by default)
bot.initialize()

# Send a message to the channel
bot.send_message_sync("Hello from the bot!")

# Cleanup when done
bot.shutdown()
```

### With Explicit Settings

```python
from telegram_bot import TelegramBot, Settings

bot = TelegramBot.get_instance()
bot.initialize(settings=Settings(
    bot_token="your_token",
    channel_id="@your_channel",
))

bot.send_message_sync("Hello!")
bot.shutdown()
```

### Receiving Messages

```python
from telegram_bot import TelegramBot

def message_handler(update):
    """Handle incoming messages."""
    if update.message:
        print(f"Received: {update.message.text}")
        # Reply to the user
        bot.reply_to_user(
            "Got your message!",
            chat_id=update.message.chat_id
        )

bot = TelegramBot.get_instance()
bot.initialize()

# Add handler (automatically starts receiving)
bot.add_message_handler(message_handler)

# Keep the program running
import time
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    bot.shutdown()
```

### Sending URLs with Base URL

The `send_url_sync` method allows you to send URLs by only specifying the path. It automatically prepends the `TELEGRAM_BASE_URL` configured in your settings. This is useful when you frequently send links to the same domain (e.g., dashboard links, reports).

```python
# With TELEGRAM_BASE_URL=https://your-server.com

bot.send_url_sync("/api/report/123")
# Sends: "https://your-server.com/api/report/123"

bot.send_url_sync("/dashboard")
# Sends: "https://your-server.com/dashboard"
```

If `TELEGRAM_BASE_URL` is empty, only the path is sent. For full URLs, use `send_message_sync()` instead.

### Direct Messages

```python
# Send a message to a specific user
bot.reply_to_user("Hello user!", chat_id=123456789)
```

## API Reference

### TelegramBot

| Method | Description |
|--------|-------------|
| `get_instance()` | Get the singleton instance |
| `reset_instance()` | Reset the singleton (for testing) |
| `initialize(settings?, env_path?)` | Initialize the bot |
| `add_message_handler(handler)` | Add a message handler |
| `remove_message_handler(handler)` | Remove a message handler |
| `clear_handlers()` | Remove all handlers |
| `start_receiving()` | Start polling for messages |
| `stop_receiving()` | Stop polling |
| `send_message_sync(message)` | Send message to channel |
| `reply_to_user(message, chat_id)` | Send direct message |
| `send_url_sync(path)` | Send URL with base prefix |
| `shutdown()` | Cleanup and shutdown |

### Settings

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `bot_token` | str | required | Telegram bot token |
| `channel_id` | str | required | Channel ID or @username |
| `base_url` | str | "" | Base URL for send_url_sync |
| `parse_mode` | str | "HTML" | Message parse mode |
| `poll_timeout` | int | 30 | Polling timeout seconds |
| `retry_delay` | float | 5.0 | Retry delay on errors |
| `send_delay` | float | 0.1 | Delay between sends |

### Exceptions

| Exception | Description |
|-----------|-------------|
| `TelegramBotError` | Base exception |
| `ConfigurationError` | Configuration issues |
| `NotInitializedError` | Bot not initialized |
| `HandlerError` | Handler execution error |

## Development

```bash
# Run tests
uv run pytest tests/ -v

# Run linter
uv run ruff check src/ tests/

# Run type checker
uv run mypy src/

# Format code
uv run ruff format src/ tests/
```

## License

MIT
