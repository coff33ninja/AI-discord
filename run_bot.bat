@echo off
title Coffee - Tsundere AI Discord Bot
echo Starting Coffee - Tsundere AI Discord Bot...
echo.
echo Press Ctrl+C to stop the bot
echo Close this window to force stop
echo.

:start
python bot.py
echo.
echo Bot stopped. Press any key to restart, or close window to exit.
pause >nul
goto start