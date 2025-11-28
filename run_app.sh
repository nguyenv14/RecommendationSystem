#!/bin/bash
# Script khởi động Unified Application (v3.0)
# KHÔNG tự động sync data - dùng scripts riêng cho RAG và Recommendation

set -e

echo "=========================================="
echo "🚀 Unified Hotel System v3.0"
echo "=========================================="

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check Docker (CHỈ Qdrant, MySQL, Redis - KHÔNG Ollama)
echo -e "${BLUE}📦 Checking Docker services...${NC}"

if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker not installed!${NC}"
    exit 1
fi

# Start Docker services (CHỈ Qdrant, MySQL, Redis)
echo -e "${BLUE}🔄 Starting Docker services (Qdrant, MySQL, Redis)...${NC}"

if docker compose version &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
else
    DOCKER_COMPOSE="docker-compose"
fi

# Start chỉ services cần thiết (KHÔNG Ollama)
$DOCKER_COMPOSE up -d qdrant mysql redis phpmyadmin

echo -e "${GREEN}✅ Docker services started${NC}"

# Wait for services
echo -e "${BLUE}⏳ Waiting for services...${NC}"
sleep 5

# Check Ollama local
echo -e "${BLUE}🤖 Checking Ollama (local)...${NC}"
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Ollama is running locally${NC}"
else
    echo -e "${YELLOW}⚠️  Ollama not running! Please start Ollama first.${NC}"
fi

# Check venv
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Creating virtual environment...${NC}"
    python -m venv venv
fi

# Activate venv
echo -e "${BLUE}🔄 Activating virtual environment...${NC}"
source venv/bin/activate || source venv/Scripts/activate

# Install dependencies
echo -e "${BLUE}📦 Installing dependencies...${NC}"
pip install -r requirements.txt -q

# Set environment
export QDRANT_URL="http://localhost:6333"
export OLLAMA_URL="http://localhost:11434"
export PORT="5000"
export AUTO_INDEX_DATA="true"  # Set to "true" to auto-index data

echo ""
echo -e "${GREEN}=========================================="
echo "🔧 Setup Collections"
echo "==========================================${NC}"

# Run setup to create collections (không index data)
python setup_collections.py

echo ""
echo -e "${GREEN}=========================================="
echo "🎉 Starting Application v3.0"
echo "==========================================${NC}"
echo ""

# Run app
python app.py

