@echo off
title Discord AI Bot
echo Starting Discord AI Bot...
echo.
echo Commands:
echo - Press Ctrl+C to stop the bot
echo - Use !shutdown in Discord to stop remotely
echo - Use !restart in Discord to restart remotely
echo - Close this window to force stop
echo.

REM Check for .venv folder first
if exist ".venv\Scripts\activate.bat" (
    echo Activating virtual environment: .venv
    call .venv\Scripts\activate.bat
    goto run
)

REM Check for venv folder
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment: venv
    call venv\Scripts\activate.bat
    goto run
)

REM Check for .env folder
if exist ".env\Scripts\activate.bat" (
    echo Activating virtual environment: .env
    call .env\Scripts\activate.bat
    goto run
)

REM Check for env folder
if exist "env\Scripts\activate.bat" (
    echo Activating virtual environment: env
    call env\Scripts\activate.bat
    goto run
)

REM If no venv found, warn user and continue with system python
echo Warning: No virtual environment found (.venv, venv, .env, or env)
echo Using system Python instead
echo.

:run
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