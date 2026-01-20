@echo off
echo Running tests...
echo.

uv run pytest tests/ -v --tb=short
