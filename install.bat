@echo off
echo Installing telegram-bot...
echo.

uv sync
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: uv sync failed
    pause
    exit /b 1
)

echo.
echo Running tests...
call tools\tests.bat
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Tests failed
    pause
    exit /b 1
)

echo.
echo Installation complete!
pause
