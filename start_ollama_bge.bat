@echo off
echo Starting Ollama services...

:: Start Ollama if not running
docker start ollama 2>nul
if errorlevel 1 (
    echo Starting Ollama container...
    docker-compose up -d ollama
    timeout /t 5
)

echo.
echo Pulling BGE-M3 model (this may take a while)...
echo Note: Since BGE-M3 is not a standard Ollama model, we'll use it with sentence-transformers
echo.
echo Alternative: Using BGE-M3 directly with sentence-transformers...
echo.
pause

