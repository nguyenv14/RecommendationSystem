@echo off
echo Starting Qdrant with Docker Compose...
docker-compose up -d
echo.
echo Qdrant is running on http://localhost:6333
echo Dashboard: http://localhost:6333/dashboard
echo.
pause

