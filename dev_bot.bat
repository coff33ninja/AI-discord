@echo off
title Discord AI Bot - Development Mode
echo Discord AI Bot - Development Mode
echo.
echo This will auto-restart the bot when you make changes to .py files
echo Press Ctrl+C to stop
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
echo Warning: No virtual environment found (venv or env)
echo Using system Python instead
echo.

:run
python dev_bot.py
pause