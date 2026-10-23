@echo off
setlocal EnableExtensions
cd /d "%~dp0"

title MT5 AI Autobot

echo ==========================================
echo          MT5 AI AUTOBOT
echo       ONE-CLICK SETUP + START
echo ==========================================
echo.

REM ---- Python check ----
where py >nul 2>nul
if errorlevel 1 (
    echo ERROR: Python 3.11+ was not found.
    echo Install Python 3.11+ and run this file again.
    pause
    exit /b 1
)

REM ---- Create virtual environment if missing ----
if not exist "%~dp0.venv\Scripts\python.exe" (
    echo [1/4] Creating Python environment...
    py -3 -m venv "%~dp0.venv"
    if errorlevel 1 (
        echo ERROR: Could not create Python environment.
        pause
        exit /b 1
    )
) else (
    echo [1/4] Python environment already ready.
)

REM ---- Install/update dependencies ----
echo [2/4] Installing required packages...
"%~dp0.venv\Scripts\python.exe" -m pip install --disable-pip-version-check -q -r "%~dp0requirements.txt"
if errorlevel 1 (
    echo ERROR: Package installation failed.
    echo Run this file again after checking the error above.
    pause
    exit /b 1
)

REM ---- Create .env only if missing ----
if not exist "%~dp0.env" (
    copy /Y "%~dp0.env.example" "%~dp0.env" >nul
    echo.
    echo [3/4] .env created from .env.example.
    echo.
    echo IMPORTANT: Open .env and add your Google AI Studio API key.
    echo Then run this same start.bat again.
    echo.
    pause
    exit /b 0
)

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
