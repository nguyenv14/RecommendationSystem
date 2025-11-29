@echo off
REM Script khởi động Unified Service (RAG + Recommendation) - Windows version

echo ==========================================
echo Unified Service (RAG + Recommendation)
echo ==========================================

REM Check Docker
where docker >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Docker is not installed!
    echo Please install Docker Desktop: https://docs.docker.com/desktop/install/windows-install/
    pause
    exit /b 1
)

REM Check Docker Compose
docker compose version >nul 2>nul
if %errorlevel% equ 0 (
    set DOCKER_COMPOSE=docker compose
) else (
    docker-compose --version >nul 2>nul
    if %errorlevel% equ 0 (
        set DOCKER_COMPOSE=docker-compose
    ) else (
        echo [ERROR] Docker Compose is not installed!
        pause
        exit /b 1
    )
)

REM Start Docker services
echo.
echo Starting Docker services (Qdrant, MySQL, Redis, Ollama)...
%DOCKER_COMPOSE% up -d

if %errorlevel% neq 0 (
    echo [ERROR] Failed to start Docker services
    pause
    exit /b 1
)

echo [OK] Docker services started

REM Wait for services
echo.
echo Waiting for services to be ready (this may take a minute)...
timeout /t 15 /nobreak >nul

REM Check if virtual environment exists
if not exist "venv\" (
    echo.
    echo Virtual environment not found. Creating one...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created
)

REM Activate virtual environment
echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/update requirements
echo.
echo Installing/updating Python dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

echo [OK] Dependencies installed

REM Set environment variables
set QDRANT_URL=http://localhost:6333
set OLLAMA_URL=http://localhost:11434
set REDIS_URL=redis://localhost:6380
set MYSQL_HOST=localhost
set MYSQL_PORT=3308
set MYSQL_USER=root
set MYSQL_PASSWORD=root
set MYSQL_DATABASE=myhotel
set PORT=5000
set DEBUG=True
set EMBEDDING_MODEL=bge-m3
set LLM_MODEL=qwen3
set COLLECTION_NAME=hotels
set LLM_PROVIDER=ollama
set AUTO_INDEX_COUPONS=true

echo.
echo ==========================================
echo Starting Unified API Service
echo ==========================================
echo.
echo Service endpoints:
echo   Main:            http://localhost:5000
echo   Health Check:    http://localhost:5000/health
echo   Status:          http://localhost:5000/api/status
echo.
echo RAG Endpoints:
echo   Chat:            POST http://localhost:5000/api/chat
echo   Search:          POST http://localhost:5000/api/search
echo.
echo Recommendation Endpoints:
echo   Similar Hotels:  GET  http://localhost:5000/api/hotels/^<id^>/similar
echo   Search Hotels:   POST http://localhost:5000/api/hotels/search
echo   Process Hotel:   POST http://localhost:5000/api/hotels/process
echo.
echo Infrastructure:
echo   Qdrant:          http://localhost:6333/dashboard
echo   phpMyAdmin:      http://localhost:8181
echo   Redis:           localhost:6380
echo.
echo ==========================================
echo.

REM Start the unified service
python unified_api_service.py

