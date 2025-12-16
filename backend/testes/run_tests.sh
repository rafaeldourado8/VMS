#!/bin/bash
# Script para executar testes do GT-Vision Backend

set -e

echo "🧪 GT-Vision Backend Test Suite"
echo "================================"
echo ""

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função para executar testes
run_tests() {
    local category=$1
    local path=$2
    
    echo -e "${YELLOW}Running $category tests...${NC}"
    if pytest "$path" -v --tb=short; then
        echo -e "${GREEN}✓ $category tests passed${NC}"
        echo ""
        return 0
    else
        echo -e "${RED}✗ $category tests failed${NC}"
        echo ""
        return 1
    fi
}

# Verificar se pytest está instalado
if ! command -v pytest &> /dev/null; then
    echo -e "${RED}pytest not found. Installing...${NC}"
    pip install pytest pytest-django pytest-cov pytest-xdist
fi

# Menu de opções
if [ "$1" == "all" ] || [ -z "$1" ]; then
    echo "Running ALL tests..."
    echo ""
    
    run_tests "CRUD" "testes/crud/"
    run_tests "Security" "testes/seguranca/"
    run_tests "Performance" "testes/velocidade/"
    run_tests "Persistence" "testes/persistencia/"
    run_tests "Streaming" "testes/streaming/"
    run_tests "Load" "testes/carga/"
    
    echo ""
    echo -e "${GREEN}✅ All test suites completed!${NC}"
    
elif [ "$1" == "crud" ]; then
    run_tests "CRUD" "testes/crud/"
    
elif [ "$1" == "security" ]; then
    run_tests "Security" "testes/seguranca/"
    
elif [ "$1" == "performance" ]; then
    run_tests "Performance" "testes/velocidade/"
    
elif [ "$1" == "persistence" ]; then
    run_tests "Persistence" "testes/persistencia/"
    
elif [ "$1" == "streaming" ]; then
    run_tests "Streaming" "testes/streaming/"
    
elif [ "$1" == "load" ]; then
    run_tests "Load" "testes/carga/"
    
elif [ "$1" == "coverage" ]; then
    echo "Running tests with coverage..."
    pytest testes/ --cov=apps --cov-report=html --cov-report=term
    echo ""
    echo -e "${GREEN}Coverage report generated in htmlcov/index.html${NC}"
    
elif [ "$1" == "quick" ]; then
    echo "Running quick tests (excluding load tests)..."
    pytest testes/ -v --ignore=testes/carga/
    
elif [ "$1" == "critical" ]; then
    echo "Running critical tests only..."
    pytest testes/seguranca/ testes/crud/test_cameras_crud.py::TestCamerasCRUD::test_create_camera -v
    
else
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
fi
