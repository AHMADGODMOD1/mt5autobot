@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (echo Python 3.11+ not found.&pause&exit /b 1)
if not exist ".venv\Scripts\python.exe" py -3 -m venv .venv
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if not exist ".env" copy /Y ".env.example" ".env" >nul
echo Setup complete. Edit .env, then run start.bat
pause
