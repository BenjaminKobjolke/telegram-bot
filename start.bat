@echo off
echo Starting telegram-bot example...
echo.

uv run python -c "from telegram_bot import TelegramBot; bot = TelegramBot.get_instance(); bot.initialize(); print('Bot initialized successfully!'); bot.shutdown()"

pause
