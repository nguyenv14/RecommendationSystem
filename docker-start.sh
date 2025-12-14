#!/bin/bash
# Quick start script for Docker containers

echo "🚀 Starting Unified API Service (RAG + Recommendation)"
echo "=================================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is not installed. Please install it first."
    exit 1
fi

# Create logs directory if it doesn't exist
mkdir -p logs

echo ""
echo "📦 Building and starting containers..."
echo ""

# Build and start services
docker-compose up -d --build

echo ""
echo "⏳ Waiting for services to be healthy..."
sleep 10

# Check service status
echo ""
echo "📊 Service Status:"
docker-compose ps

echo ""
echo "✅ Services started!"
echo ""
echo "📡 API Endpoints:"
echo "   Health:     http://localhost:5000/health"
echo "   RAG Chat:   POST http://localhost:5000/api/chat"
echo "   Recommend:  POST http://localhost:5000/api/recommend/query"
echo ""
echo "🔍 View logs:"
echo "   docker-compose logs -f unified_api"
echo ""
echo "🛑 Stop services:"
echo "   docker-compose down"
echo ""

