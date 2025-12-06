#!/bin/bash
# Script khởi động với LM Studio (qwen/qwen3-4b-2507)

# set -e  # Commented out to avoid early exit on minor errors

echo "=========================================="
echo "🚀 Unified Hotel System - LM Studio"
echo "=========================================="

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# ============================================
# Step 0: Tìm Python 3.9
# ============================================
echo -e "${BLUE}🐍 Checking Python 3.9...${NC}"

# Try to find Python 3.9 specifically
PYTHON_CMD=""
# Try different Python 3.9 commands
if command -v python3.9 &> /dev/null; then
    PYTHON_CMD="python3.9"
elif command -v py &> /dev/null && py -3.9 --version &> /dev/null; then
    PYTHON_CMD="py -3.9"
elif python --version 2>&1 | grep -q "3\.9"; then
    PYTHON_CMD="python"
elif python3 --version 2>&1 | grep -q "3\.9"; then
    PYTHON_CMD="python3"
else
    echo -e "${RED}❌ Python 3.9 not found!${NC}"
    echo "Please install Python 3.9:"
    echo "  Windows: Download from https://www.python.org/downloads/"
    echo "  Or use: py -3.9 (if Python Launcher is installed)"
    exit 1
fi

# Verify it's actually Python 3.9
PYTHON_VERSION=$($PYTHON_CMD --version 2>&1)
if ! echo "$PYTHON_VERSION" | grep -q "3\.9"; then
    echo -e "${YELLOW}⚠️  Warning: $PYTHON_VERSION is not Python 3.9${NC}"
    echo -e "${YELLOW}   Continuing anyway, but Python 3.9 is recommended${NC}"
fi
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

# Start Docker services
echo -e "${BLUE}🔄 Starting Docker services (Qdrant, MySQL, Redis)...${NC}"

if docker compose version &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
else
    DOCKER_COMPOSE="docker-compose"
fi

$DOCKER_COMPOSE up -d qdrant mysql redis phpmyadmin

echo -e "${GREEN}✅ Docker services started${NC}"

# Wait for services
echo -e "${BLUE}⏳ Waiting for services...${NC}"
sleep 5

# ============================================
# Step 2: Check LM Studio
# ============================================
echo -e "${BLUE}🤖 Checking LM Studio...${NC}"

LM_STUDIO_URL="http://127.0.0.1:1234"

if curl -s "$LM_STUDIO_URL/v1/models" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ LM Studio is running${NC}"
    
    # List models
    echo -e "${BLUE}📋 Available models:${NC}"
    MODELS=$(curl -s "$LM_STUDIO_URL/v1/models" | $PYTHON_CMD -c "import sys, json; models = json.load(sys.stdin); print('\n'.join([f'   - {m[\"id\"]}' for m in models.get('data', [])]))" 2>/dev/null)
    if [ -n "$MODELS" ]; then
        echo "$MODELS"
    else
        echo "   (Could not list models)"
    fi
else
    echo -e "${RED}❌ LM Studio is not running!${NC}"
    echo ""
    echo "Please start LM Studio:"
    echo "  1. Open LM Studio"
    echo "  2. Load model: qwen/qwen3-4b-2507"
    echo "  3. Go to 'Developer' tab"
    echo "  4. Click 'Start Server' at $LM_STUDIO_URL"
    echo ""
    exit 1
fi

# Check Ollama (for embeddings)
echo -e "${BLUE}🤖 Checking Ollama (for embeddings)...${NC}"
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Ollama is running (for embeddings)${NC}"
else
    echo -e "${YELLOW}⚠️  Ollama not running! RAG embeddings will fail.${NC}"
    echo "   Please start Ollama: ollama serve"
fi

# ============================================
# Step 3: Setup venv
# ============================================
RECREATE_VENV=false

if [ -d "venv" ]; then
    echo -e "${GREEN}✅ venv already exists${NC}"

    # Determine Python inside existing venv
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" || -f "venv/Scripts/python.exe" || -f "venv/Scripts/python" ]]; then
        VENV_PYTHON="venv/Scripts/python"
    else
        VENV_PYTHON="venv/bin/python"
    fi

    # If venv has Python, check its version; recreate if not 3.9
    if [ -x "$VENV_PYTHON" ]; then
        VENV_VERSION=$($VENV_PYTHON --version 2>&1 || echo "")
        if [ -n "$VENV_VERSION" ] && ! echo "$VENV_VERSION" | grep -q "3\.9"; then
            echo -e "${YELLOW}⚠️  venv Python version ($VENV_VERSION) is not 3.9, will recreate...${NC}"
            RECREATE_VENV=true
        fi
    fi

    # Check if pip exists in venv (only if we haven't already decided to recreate)
    if [ "$RECREATE_VENV" = false ]; then
        if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" || -f "venv/Scripts/activate" ]]; then
            if [ ! -f "venv/Scripts/pip.exe" ] && [ ! -f "venv/Scripts/pip" ]; then
                echo -e "${YELLOW}⚠️  venv missing pip, will recreate...${NC}"
                RECREATE_VENV=true
            fi
        else
            if [ ! -f "venv/bin/pip" ]; then
                echo -e "${YELLOW}⚠️  venv missing pip, will recreate...${NC}"
                RECREATE_VENV=true
            fi
        fi
    fi
else
    echo -e "${BLUE}📦 Creating virtual environment...${NC}"
    RECREATE_VENV=true
fi

if [ "$RECREATE_VENV" = true ]; then
    # Remove old venv if exists
    if [ -d "venv" ]; then
        echo -e "${YELLOW}🗑️  Removing old venv...${NC}"
        rm -rf venv
    fi
    echo -e "${BLUE}📦 Creating new virtual environment...${NC}"
    $PYTHON_CMD -m venv venv --clear
    echo -e "${GREEN}✅ venv created${NC}"
fi

# Activate venv
echo -e "${BLUE}🔄 Activating virtual environment...${NC}"
# Detect OS and use correct activation script
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" || -f "venv/Scripts/activate" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Verify Python version in venv
ACTIVE_PYTHON_VERSION=$(python --version 2>&1)
PYTHON_PATH=$(which python || where python 2>/dev/null | head -1)
echo -e "${GREEN}✅ venv Python: $ACTIVE_PYTHON_VERSION${NC}"
echo -e "${BLUE}   Python path: $PYTHON_PATH${NC}"

# Ensure pip is available
if ! python -m pip --version &> /dev/null; then
    echo -e "${YELLOW}⚠️  pip not available, installing...${NC}"
    python -m ensurepip --upgrade
    python -m pip install --upgrade pip setuptools wheel
fi

# Check if dependencies are installed
echo -e "${BLUE}🔍 Checking dependencies...${NC}"
DEPS_OK=true
python -c "import flask" 2>/dev/null || DEPS_OK=false
python -c "import qdrant_client" 2>/dev/null || DEPS_OK=false
python -c "import langchain" 2>/dev/null || DEPS_OK=false
python -c "import pandas" 2>/dev/null || DEPS_OK=false
python -c "import openai" 2>/dev/null || DEPS_OK=false  # For LM Studio
python -c "import colorlog" 2>/dev/null || DEPS_OK=false  # Check colorlog too

if [ "$DEPS_OK" = true ]; then
    echo -e "${GREEN}✅ All core dependencies installed${NC}"
    # Always upgrade langchain packages for qdrant compatibility
else
    echo -e "${YELLOW}⚠️  Some dependencies missing, installing all...${NC}"
    echo -e "${BLUE}📦 Installing/upgrading dependencies from requirements-python39.txt...${NC}"
    python -m pip install --upgrade pip setuptools wheel -q
    if python -m pip install -r requirements-python39.txt; then
        echo -e "${GREEN}✅ Dependencies installed${NC}"
    else
        echo -e "${RED}❌ Failed to install dependencies from requirements-python39.txt${NC}"
        echo -e "${RED}   Please check the error above and try again.${NC}"
        exit 1
    fi
fi

# Always verify and install critical dependencies to ensure they're present
echo -e "${BLUE}🔍 Verifying critical dependencies...${NC}"
MISSING_DEPS=""
python -c "import flask" 2>/dev/null || MISSING_DEPS="$MISSING_DEPS flask"
python -c "import colorlog" 2>/dev/null || MISSING_DEPS="$MISSING_DEPS colorlog"
python -c "import qdrant_client" 2>/dev/null || MISSING_DEPS="$MISSING_DEPS qdrant-client"
python -c "import pandas" 2>/dev/null || MISSING_DEPS="$MISSING_DEPS pandas"
python -c "import openai" 2>/dev/null || MISSING_DEPS="$MISSING_DEPS openai"
python -c "import langchain" 2>/dev/null || MISSING_DEPS="$MISSING_DEPS langchain"

if [ -n "$MISSING_DEPS" ]; then
    echo -e "${RED}❌ Missing critical dependencies:$MISSING_DEPS${NC}"
    echo -e "${BLUE}📦 Installing missing dependencies...${NC}"
    if python -m pip install $MISSING_DEPS; then
        echo -e "${GREEN}✅ Missing dependencies installed${NC}"
    else
        echo -e "${RED}❌ Failed to install some critical dependencies:$MISSING_DEPS${NC}"
        echo -e "${RED}   Please check the error above and try running the script again.${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✅ All critical dependencies verified${NC}"
fi

# ============================================
# Step 4: Set environment variables - LM STUDIO
# ============================================
export QDRANT_URL="http://localhost:6333"
export OLLAMA_URL="http://localhost:11434"  # Still for embeddings
export PORT="5000"
export AUTO_INDEX_DATA="false"

# ⭐ LM STUDIO CONFIGURATION
export LLM_PROVIDER="lm_studio"
export LM_STUDIO_URL="http://127.0.0.1:1234"
export LLM_MODEL="qwen/qwen3-4b-2507"

# LM Studio doesn't need real API key, but set dummy to avoid errors
export OPENAI_API_KEY="lm-studio-dummy-key"

# Prevent PyTorch from loading
export TRANSFORMERS_OFFLINE=1
export HF_HUB_OFFLINE=1
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
# Step 6: Start Application with LM Studio
# ============================================
echo ""
echo -e "${GREEN}=========================================="
echo "🎉 Starting Application - LM Studio Mode"
echo "==========================================${NC}"
echo -e "${BLUE}📍 URL: http://localhost:5000${NC}"
echo -e "${YELLOW}🤖 LLM: LM Studio (qwen/qwen3-4b-2507)${NC}"
echo -e "${YELLOW}🔢 Embeddings: Ollama (bge-m3)${NC}"
echo -e "${YELLOW}💡 Press Ctrl+C to stop${NC}"
echo ""

# Run app
python app.py

