#!/bin/bash
# Quick start script for RAG Docker services

set -e

echo "🚀 Starting RAG Docker Services..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if Ollama is running (optional check)
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "⚠️  Warning: Ollama is not running on port 11434"
    echo "   Make sure Ollama is running on host: http://localhost:11434"
fi

# Start services
echo "📦 Starting Qdrant and Redis..."
docker-compose up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."
sleep 5

# Check Qdrant health
echo "🔍 Checking Qdrant health..."
if curl -s http://localhost:6333/health > /dev/null 2>&1; then
    echo "✅ Qdrant is healthy"
else
    echo "❌ Qdrant health check failed"
    docker-compose logs qdrant
    exit 1
fi

# Check Redis health
echo "🔍 Checking Redis health..."
if docker exec redis_rag redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis is healthy"
else
    echo "⚠️  Redis health check failed (optional service)"
fi

# Show status
echo ""
echo "📊 Services Status:"
docker-compose ps

echo ""
echo "✅ Services are running!"
echo ""
echo "📝 Useful commands:"
echo "   View logs:    docker-compose logs -f"
echo "   Stop services: docker-compose down"
echo "   Qdrant dashboard: http://localhost:6333/dashboard"
echo ""

