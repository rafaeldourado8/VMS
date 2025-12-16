#!/bin/bash
# Script para executar testes via Docker Compose

set -e

echo "🧪 GT-Vision Backend Test Suite (Docker)"
echo "========================================="
echo ""

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Verificar se containers estão rodando
if ! docker-compose ps | grep -q "Up"; then
    echo -e "${YELLOW}Iniciando containers...${NC}"
    docker-compose up -d postgres_db redis_cache
    sleep 5
fi

# Função para executar testes
run_tests() {
    local category=$1
    local path=$2
    
    echo -e "${YELLOW}Running $category tests...${NC}"
    if docker-compose exec -T backend pytest "$path" -v --tb=short; then
        echo -e "${GREEN}✓ $category tests passed${NC}"
        echo ""
        return 0
    else
        echo -e "${RED}✗ $category tests failed${NC}"
        echo ""
        return 1
    fi
}

# Menu de opções
case "$1" in
    "all"|"")
        echo "Running ALL tests..."
        echo ""
        docker-compose exec -T backend pytest testes/ -v
        ;;
    
    "crud")
        run_tests "CRUD" "testes/crud/"
        ;;
    
    "security")
        run_tests "Security" "testes/seguranca/"
        ;;
    
    "performance")
        run_tests "Performance" "testes/velocidade/"
        ;;
    
    "persistence")
        run_tests "Persistence" "testes/persistencia/"
        ;;
    
    "streaming")
        run_tests "Streaming" "testes/streaming/"
        ;;
    
    "load")
        run_tests "Load" "testes/carga/"
        ;;
    
    "coverage")
        echo "Running tests with coverage..."
        docker-compose exec -T backend pytest testes/ --cov=apps --cov-report=html --cov-report=term
        echo ""
        echo -e "${GREEN}Coverage report generated in backend/htmlcov/index.html${NC}"
        ;;
    
    "quick")
        echo "Running quick tests (excluding load tests)..."
        docker-compose exec -T backend pytest testes/ -v --ignore=testes/carga/
        ;;
    
    "critical")
        echo "Running critical tests only..."
        docker-compose exec -T backend pytest testes/seguranca/ testes/crud/test_cameras_crud.py::TestCamerasCRUD::test_create_camera -v
        ;;
    
    *)
        echo "Usage: ./run_tests.sh [option]"
        echo ""
        echo "Options:"
        echo "  all          - Run all tests (default)"
        echo "  crud         - Run CRUD tests"
        echo "  security     - Run security tests"
        echo "  performance  - Run performance tests"
        echo "  persistence  - Run persistence tests"
        echo "  streaming    - Run streaming tests"
        echo "  load         - Run load tests"
        echo "  coverage     - Run with coverage report"
        echo "  quick        - Run quick tests (no load)"
        echo "  critical     - Run critical tests only"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}✅ Tests completed!${NC}"
