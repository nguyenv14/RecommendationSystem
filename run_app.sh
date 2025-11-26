#!/bin/bash
# Script khởi động Unified Application (v3.0)

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

# Check Docker
echo -e "${BLUE}📦 Checking Docker services...${NC}"

if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker not installed!${NC}"
    exit 1
fi

# Start Docker services
echo -e "${BLUE}🔄 Starting Docker services...${NC}"

if docker compose version &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
else
    DOCKER_COMPOSE="docker-compose"
fi

$DOCKER_COMPOSE up -d

echo -e "${GREEN}✅ Docker services started${NC}"

# Wait for services
echo -e "${BLUE}⏳ Waiting for services...${NC}"
sleep 10

# Check venv
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate venv
echo -e "${BLUE}🔄 Activating virtual environment...${NC}"
source venv/bin/activate || source venv/Scripts/activate

# Install dependencies
echo -e "${BLUE}📦 Installing dependencies...${NC}"
pip install -r requirements.txt --quiet

# Set environment
export QDRANT_URL="http://localhost:6333"
export OLLAMA_URL="http://localhost:11434"
export PORT="5000"

echo ""
echo -e "${GREEN}=========================================="
echo "🎉 Starting Application v3.0"
echo "==========================================${NC}"
echo ""

# Run app
python app.py

