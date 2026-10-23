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
    echo Setup failed.
    pause
    exit /b 1
  )
)

if not exist ".venv\Scripts\python.exe" (
  echo Setup finished but .venv was not found.
  echo Rebuilding the virtual environment directly...
  echo.

  py -3 -m venv "%~dp0.venv"
  if errorlevel 1 (
    echo.
    echo Could not create the Python virtual environment.
    echo Please send the exact error shown above.
    pause
    exit /b 1
  )

  call "%~dp0.venv\Scripts\activate.bat"
  python -m pip install --upgrade pip
  python -m pip install -r "%~dp0requirements.txt"
  if errorlevel 1 (
    echo.
    echo Package installation failed.
    pause
    exit /b 1
  )
)

if not exist ".env" (
  copy /Y ".env.example" ".env" >nul
  echo.
  echo .env was created.
  echo Add your Google AI Studio API key to .env, save it, then run start.bat again.
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
