@echo off
title Coffee - Tsundere AI Discord Bot
echo Starting Coffee - Tsundere AI Discord Bot...
echo.
echo Commands:
echo - Press Ctrl+C to stop the bot
echo - Use !shutdown in Discord to stop remotely
echo - Use !restart in Discord to restart remotely
echo - Close this window to force stop
echo.

:start
python bot.py
set exit_code=%ERRORLEVEL%

if %exit_code%==0 (
    echo.
    echo Bot shut down normally.
    echo Press any key to restart, or close window to exit.
    pause >nul
    goto start
) else (
    echo.
    echo Bot crashed with exit code %exit_code%
    echo Press any key to restart, or close window to exit.
    pause >nul
    goto start
)