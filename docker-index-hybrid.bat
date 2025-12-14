@echo off
REM Script to run hybrid indexing inside Docker container (Windows)

echo 🔧 Running Hybrid Search Indexing in Docker container...
echo ==================================================

REM Check if container is running
docker ps | findstr unified_api >nul
if errorlevel 1 (
    echo ❌ Error: unified_api container is not running
    echo    Please start it first: docker-compose up -d
    exit /b 1
)

echo.
echo 📊 This will:
echo    1. Create dense embeddings (semantic) from Ollama
echo    2. Create sparse embeddings (BM25) from fastembed
echo    3. Upload to Qdrant with hybrid vectors
echo.
echo ⚠️  This may take 5-10 minutes depending on data size
echo.
set /p confirm="Continue? (y/n): "

if /i not "%confirm%"=="y" (
    echo Cancelled.
    exit /b 0
)

echo.
echo 🚀 Running index_with_hybrid.py in container...
echo.

REM Run index script in container
docker-compose exec unified_api python index_with_hybrid.py

echo.
echo ✅ Done!
echo.
echo 💡 To check collections status:
echo    docker-compose exec unified_api python -c "from src.core import VectorStoreService; from src.config import get_settings; vs = VectorStoreService(url=get_settings().QDRANT_URL); [print(f'{c.name}: {vs.client.get_collection(c.name).points_count} points') for c in vs.client.get_collections().collections]"

pause


