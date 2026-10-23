@echo off
setlocal
cd /d "%~dp0"

echo ==========================================
echo       MT5 AI AUTOBOT - START
echo ==========================================
echo.

where py >nul 2>nul
if errorlevel 1 (
  echo Python 3.11+ not found.
  echo Install Python 3.11+ and try again.
  pause
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  echo First-time setup required. Starting setup automatically...
  echo.
  call "%~dp0setup.bat"
  if errorlevel 1 (
    echo.
    echo Setup failed. Please check the message above.
    pause
    exit /b 1
  )
)

if not exist ".venv\Scripts\python.exe" (
  echo Setup did not create the virtual environment.
  pause
  exit /b 1
)

if not exist ".env" (
  copy /Y ".env.example" ".env" >nul
  echo .env was created from .env.example.
  echo Add your Google AI Studio API key to .env, then run this file again.
  pause
  exit /b 0
)

call ".venv\Scripts\activate.bat"

echo.
echo Starting MT5 AI Autobot...
echo Dashboard: http://127.0.0.1:8000
echo Keep this window open while the bot is running.
echo.

python -m uvicorn app.main:app --host 127.0.0.1 --port 8000

echo.
echo Bot stopped.
pause
