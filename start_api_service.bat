@echo off
echo Starting Hotel Recommendation API Service...
echo.

REM Check if Ollama is running
echo Checking Ollama...
curl http://localhost:11434/api/tags > nul 2>&1
if errorlevel 1 (
    echo Ollama is not running. Starting Ollama...
    docker-compose up -d ollama
    timeout /t 5
)

REM Check if Qdrant is running
echo Checking Qdrant...
curl http://localhost:6333 > nul 2>&1
if errorlevel 1 (
    echo Qdrant is not running. Starting Qdrant...
    docker-compose up -d qdrant
    timeout /t 3
)

REM Start API service
echo Starting API service...
python api_service.py

pause

