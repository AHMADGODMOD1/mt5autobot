@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title MT5 AI Autobot

echo ==========================================
echo          MT5 AI AUTOBOT
echo       ONE-CLICK SETUP + START
echo ==========================================
echo.

REM Prefer the known working Python 3.12 installation.
set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"

if not exist "%PYTHON_EXE%" (
    echo ERROR: Python 3.12 was not found at:
    echo %PYTHON_EXE%
    echo.
    echo Install Python 3.12 and run this file again.
    pause
    exit /b 1
)

echo Python: %PYTHON_EXE%
"%PYTHON_EXE%" --version
if errorlevel 1 (
    echo ERROR: Python 3.12 could not be started.
    pause
    exit /b 1
)

if not exist "%~dp0.venv\Scripts\python.exe" (
    echo.
    echo [1/4] Creating Python environment...
    "%PYTHON_EXE%" -m venv "%~dp0.venv"
    if errorlevel 1 (
        echo.
        echo ERROR: Could not create Python environment.
        pause
        exit /b 1
    )
) else (
    echo [1/4] Python environment already ready.
)

echo.
echo [2/4] Installing required packages...
"%~dp0.venv\Scripts\python.exe" -m pip install --disable-pip-version-check -q -r "%~dp0requirements.txt"
if errorlevel 1 (
    echo.
    echo ERROR: Package installation failed.
    pause
    exit /b 1
)

if not exist "%~dp0.env" (
    copy /Y "%~dp0.env.example" "%~dp0.env" >nul
    echo.
    echo [3/4] .env created.
    echo Add your Google AI Studio API key to .env, then run start.bat again.
    pause
    exit /b 0
)

echo.
echo [3/4] Configuration found.
echo [4/4] Starting MT5 AI Autobot...
echo.
echo Dashboard: http://127.0.0.1:8000
echo Keep this window open while the bot is running.
echo.

"%~dp0.venv\Scripts\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8000

echo.
echo ==========================================
echo Bot stopped.
echo ==========================================
pause
