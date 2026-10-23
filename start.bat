@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (echo Run setup.bat first.&pause&exit /b 1)
if not exist ".env" copy /Y ".env.example" ".env" >nul
call .venv\Scripts\activate.bat
echo Starting MT5 AI Autobot at http://127.0.0.1:8000
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
pause
