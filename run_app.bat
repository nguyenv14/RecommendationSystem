@echo off
REM Script khởi động Unified Application (v3.0) - Windows

echo ==========================================
echo Unified Hotel System v3.0
echo ==========================================

REM Check Docker
where docker >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Docker not installed!
    pause
    exit /b 1
)

REM Start Docker services
echo.
echo Starting Docker services...
docker compose up -d
if %errorlevel% neq 0 (
    echo [ERROR] Failed to start Docker services
    pause
    exit /b 1
)

echo [OK] Docker services started

REM Wait
echo.
echo Waiting for services...
timeout /t 10 /nobreak >nul

REM Check venv
if not exist "venv\" (
    echo.
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate venv
echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo.
echo Installing dependencies...
pip install -r requirements.txt --quiet

REM Set environment
set QDRANT_URL=http://localhost:6333
set OLLAMA_URL=http://localhost:11434
set PORT=5000
set AUTO_INDEX_DATA=false

echo.
echo ==========================================
echo Setup Collections
echo ==========================================
echo.

REM Run setup
python setup_collections.py
if %errorlevel% neq 0 (
    echo [ERROR] Setup failed!
    pause
    exit /b 1
)

echo.
echo ==========================================
echo Starting Application v3.0
echo ==========================================
echo.

REM Run app
python app.py

