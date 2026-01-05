#!/bin/bash
# ======================================================
# GT-Vision VMS - Script de Inicialização
# ======================================================

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}======================================================${NC}"
echo -e "${BLUE}       GT-Vision VMS - Inicialização${NC}"
echo -e "${BLUE}======================================================${NC}"

# Verificar .env
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  Arquivo .env não encontrado. Copiando de .env.example...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}⚠️  Por favor, edite o arquivo .env com suas configurações!${NC}"
fi

# Função para verificar serviço
check_service() {
    local name=$1
    local url=$2
    local max_attempts=30
    local attempt=1
    
    echo -ne "   Aguardando $name"
    while [ $attempt -le $max_attempts ]; do
        if curl -sf "$url" > /dev/null 2>&1; then
            echo -e " ${GREEN}✓${NC}"
            return 0
        fi
        echo -n "."
        sleep 2
        ((attempt++))
    done
    echo -e " ${RED}✗${NC}"
    return 1
}

# 1. Iniciar infraestrutura
echo -e "\n${BLUE}[1/4] Iniciando infraestrutura...${NC}"
docker-compose up -d postgres_db redis_cache rabbitmq
sleep 5

# 2. Iniciar MediaMTX
echo -e "\n${BLUE}[2/4] Iniciando MediaMTX...${NC}"
docker-compose up -d mediamtx
check_service "MediaMTX" "http://localhost:9997/v3/config/global/get"

# 3. Iniciar serviços principais
echo -e "\n${BLUE}[3/4] Iniciando serviços principais...${NC}"
docker-compose up -d backend streaming gateway nginx
echo "   Aguardando Backend inicializar (migrações)..."
sleep 30
check_service "Backend" "http://localhost:8000/admin/login/"
check_service "Streaming" "http://localhost:8001/health"

# 4. Iniciar load balancers
echo -e "\n${BLUE}[4/4] Iniciando Kong e HAProxy...${NC}"
docker-compose up -d kong haproxy frontend
sleep 5
check_service "Kong" "http://localhost:8000/api/auth/login/"
check_service "HAProxy Stats" "http://localhost:8404/stats"

# Resumo
echo -e "\n${GREEN}======================================================${NC}"
echo -e "${GREEN}       ✅ GT-Vision VMS Iniciado!${NC}"
echo -e "${GREEN}======================================================${NC}"
echo ""
echo -e "   ${BLUE}Frontend:${NC}        http://localhost:5173"
echo -e "   ${BLUE}API:${NC}             http://localhost/api/"
echo -e "   ${BLUE}Admin Django:${NC}    http://localhost/admin/"
echo -e "   ${BLUE}Kong Manager:${NC}    http://localhost:8002"
echo -e "   ${BLUE}HAProxy Stats:${NC}   http://localhost:8404/stats"
echo -e "   ${BLUE}RabbitMQ:${NC}        http://localhost:15672"
echo -e "   ${BLUE}Streaming API:${NC}   http://localhost:8001/docs"
echo ""

# AI Service (opcional)
echo -e "${YELLOW}======================================================${NC}"
echo -e "${YELLOW}   ℹ️  AI Service (opcional)${NC}"
echo -e "${YELLOW}======================================================${NC}"
echo ""
echo "   Para iniciar o AI Service (build demora ~10-15 min):"
echo ""
echo "   cd services/ai-service"
echo "   docker-compose build   # Apenas na primeira vez"
echo "   docker-compose up -d"
echo ""
