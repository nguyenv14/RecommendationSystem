#!/bin/bash
# Script khởi động Unified Service (RAG + Recommendation)

set -e

echo "=========================================="
echo "🚀 Unified Service (RAG + Recommendation)"
echo "=========================================="

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Hàm kiểm tra service đã chạy chưa
check_service() {
    local service_name=$1
    local port=$2
    
    if command -v nc &> /dev/null; then
        nc -z localhost $port 2>/dev/null
        return $?
    elif command -v curl &> /dev/null; then
        curl -s -o /dev/null -w "%{http_code}" http://localhost:$port 2>/dev/null | grep -q "200\|302"
        return $?
    else
        # Fallback: try wget
        wget -q --spider http://localhost:$port 2>/dev/null
        return $?
    fi
}

# Kiểm tra Docker services
echo -e "${BLUE}📦 Checking Docker services...${NC}"

if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed!${NC}"
    echo "Please install Docker first: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed!${NC}"
    echo "Please install Docker Compose first"
    exit 1
fi

# Khởi động Docker services
echo -e "${BLUE}🔄 Starting Docker services (Qdrant, MySQL, Redis, Ollama)...${NC}"

# Use docker compose (newer) or docker-compose (older)
if docker compose version &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
else
    DOCKER_COMPOSE="docker-compose"
fi

$DOCKER_COMPOSE up -d

echo -e "${GREEN}✅ Docker services started${NC}"

# Đợi các services sẵn sàng
echo -e "${BLUE}⏳ Waiting for services to be ready...${NC}"

# Wait for Qdrant
echo -n "  - Waiting for Qdrant (port 6333)..."
for i in {1..30}; do
    if check_service "Qdrant" 6333; then
        echo -e " ${GREEN}✓${NC}"
        break
    fi
    sleep 2
    echo -n "."
done

# Wait for MySQL
echo -n "  - Waiting for MySQL (port 3308)..."
for i in {1..30}; do
    if check_service "MySQL" 3308; then
        echo -e " ${GREEN}✓${NC}"
        break
    fi
    sleep 2
    echo -n "."
done

# Wait for Ollama
echo -n "  - Waiting for Ollama (port 11434)..."
for i in {1..30}; do
    if check_service "Ollama" 11434; then
        echo -e " ${GREEN}✓${NC}"
        break
    fi
    sleep 2
    echo -n "."
done

echo -e "${GREEN}✅ All Docker services are ready${NC}"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found. Creating one...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
fi

# Activate virtual environment
echo -e "${BLUE}🔄 Activating virtual environment...${NC}"
source venv/bin/activate || source venv/Scripts/activate

# Install/update requirements
echo -e "${BLUE}📦 Installing/updating Python dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

echo -e "${GREEN}✅ Dependencies installed${NC}"

# Set environment variables
export QDRANT_URL="http://localhost:6333"
export OLLAMA_URL="http://localhost:11434"
export REDIS_URL="redis://localhost:6380"
export MYSQL_HOST="localhost"
export MYSQL_PORT="3308"
export MYSQL_USER="root"
export MYSQL_PASSWORD="root"
export MYSQL_DATABASE="myhotel"
export PORT="5000"
export DEBUG="True"
export EMBEDDING_MODEL="bge-m3"
export LLM_MODEL="qwen3"
export COLLECTION_NAME="hotels"
export LLM_PROVIDER="ollama"
export AUTO_INDEX_COUPONS="true"

echo ""
echo -e "${GREEN}=========================================="
echo "🎉 Starting Unified API Service"
echo "==========================================${NC}"
echo ""
echo -e "📍 Service endpoints:"
echo -e "   ${BLUE}Main:${NC}            http://localhost:5000"
echo -e "   ${BLUE}Health Check:${NC}    http://localhost:5000/health"
echo -e "   ${BLUE}Status:${NC}          http://localhost:5000/api/status"
echo ""
echo -e "🤖 ${YELLOW}RAG Endpoints:${NC}"
echo -e "   ${BLUE}Chat:${NC}            POST http://localhost:5000/api/chat"
echo -e "   ${BLUE}Search:${NC}          POST http://localhost:5000/api/search"
echo ""
echo -e "🎯 ${YELLOW}Recommendation Endpoints:${NC}"
echo -e "   ${BLUE}Similar Hotels:${NC}  GET  http://localhost:5000/api/hotels/<id>/similar"
echo -e "   ${BLUE}Search Hotels:${NC}   POST http://localhost:5000/api/hotels/search"
echo -e "   ${BLUE}Process Hotel:${NC}   POST http://localhost:5000/api/hotels/process"
echo ""
echo -e "📊 ${YELLOW}Infrastructure:${NC}"
echo -e "   ${BLUE}Qdrant:${NC}          http://localhost:6333/dashboard"
echo -e "   ${BLUE}phpMyAdmin:${NC}      http://localhost:8181"
echo -e "   ${BLUE}Redis:${NC}           localhost:6380"
echo ""
echo "=========================================="
echo ""

# Start the unified service
python unified_api_service.py

