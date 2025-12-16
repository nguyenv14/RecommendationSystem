#!/bin/bash
# Script khởi động Unified Application (v3.0) - Python 3.9
# Chạy 1 lệnh duy nhất: bash run_app.sh

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

# ============================================
# Step 0: Tìm Python có sẵn
# ============================================
echo -e "${BLUE}🐍 Checking Python...${NC}"

PYTHON_CMD=""
if command -v python3.9 &> /dev/null; then
    PYTHON_CMD="python3.9"
elif command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo -e "${RED}❌ No Python found!${NC}"
    echo "Please install Python 3.9+"
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1)
echo -e "${GREEN}✅ Found: $PYTHON_VERSION${NC}"
echo -e "${BLUE}   Using: $PYTHON_CMD${NC}"

# ============================================
# Step 1: Check Docker services
# ============================================
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

# ============================================
# Step 2: Check Ollama
# ============================================
echo -e "${BLUE}🤖 Checking Ollama (local)...${NC}"
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Ollama is running locally${NC}"
else
    echo -e "${YELLOW}⚠️  Ollama not running! Please start Ollama first.${NC}"
fi

# ============================================
# Step 3: Setup venv
# ============================================
if [ -d "venv" ]; then
    echo -e "${GREEN}✅ venv already exists${NC}"
else
    echo -e "${BLUE}📦 Creating virtual environment...${NC}"
    $PYTHON_CMD -m venv venv
    echo -e "${GREEN}✅ venv created${NC}"
fi

# Activate venv
echo -e "${BLUE}🔄 Activating virtual environment...${NC}"
source venv/bin/activate

# Verify Python version in venv
ACTIVE_PYTHON_VERSION=$(python --version 2>&1)
echo -e "${GREEN}✅ venv Python: $ACTIVE_PYTHON_VERSION${NC}"

# Check if dependencies are installed
echo -e "${BLUE}🔍 Checking dependencies...${NC}"
DEPS_OK=true
python -c "import flask" 2>/dev/null || DEPS_OK=false
python -c "import qdrant_client" 2>/dev/null || DEPS_OK=false
python -c "import langchain" 2>/dev/null || DEPS_OK=false
python -c "import pandas" 2>/dev/null || DEPS_OK=false

if [ "$DEPS_OK" = true ]; then
    echo -e "${GREEN}✅ All dependencies installed, skipping install${NC}"
else
    echo -e "${YELLOW}⚠️  Some dependencies missing${NC}"
    echo -e "${BLUE}📦 Installing dependencies...${NC}"
    pip install --upgrade pip setuptools wheel -q
    pip install -r requirements-python39.txt -q
    echo -e "${GREEN}✅ Dependencies installed${NC}"
fi

# ============================================
# Step 4: Set environment variables
# ============================================
export QDRANT_URL="http://localhost:6333"
export OLLAMA_URL="http://localhost:11434"
export PORT="5000"
export AUTO_INDEX_DATA="false"  # Chỉ tạo collections, không index data

# Prevent PyTorch from loading (not needed for Ollama embeddings)
export TRANSFORMERS_OFFLINE=1
# NOTE: HF_HUB_OFFLINE is temporarily unset in app.py to allow BM25 model download
# The app will restore it after initialization
# export HF_HUB_OFFLINE=1  # Commented out to allow hybrid search
export TORCH_DISABLE_IMPORT=1

# ============================================
# Step 5: Setup Collections
# ============================================
echo ""
echo -e "${GREEN}=========================================="
echo "🔧 Setup Collections"
echo "==========================================${NC}"
echo -e "${YELLOW}💡 Checking collections...${NC}"
echo ""

python setup_collections.py

echo ""
echo -e "${YELLOW}💡 Tip: Collections có data rồi sẽ không tải lại${NC}"

# ============================================
# Step 6: Start Application
# ============================================
echo ""
echo -e "${GREEN}=========================================="
echo "🎉 Starting Application v3.0"
echo "==========================================${NC}"
echo -e "${BLUE}📍 URL: http://localhost:5000${NC}"
echo -e "${YELLOW}💡 Press Ctrl+C to stop${NC}"
echo ""

# Run app
python app.py

