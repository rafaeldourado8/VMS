#!/bin/bash
# Script de teste do Kong API Gateway

set -e

echo "🧪 Testando Kong API Gateway..."
echo ""

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função de teste
test_endpoint() {
    local name=$1
    local url=$2
    local expected_code=$3
    
    echo -n "Testing $name... "
    
    response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || echo "000")
    
    if [ "$response" = "$expected_code" ]; then
        echo -e "${GREEN}✓ OK${NC} (HTTP $response)"
    else
        echo -e "${RED}✗ FAIL${NC} (Expected $expected_code, got $response)"
    fi
}

echo "=== Kong Health Checks ==="
test_endpoint "Kong Proxy" "http://localhost:8000/" "404"
test_endpoint "Kong Admin API" "http://localhost:8001/" "200"
test_endpoint "Kong Manager GUI" "http://localhost:8002/" "200"
echo ""

echo "=== API Routes via Kong ==="
test_endpoint "Django API (via Kong)" "http://localhost:8000/api/" "200"
test_endpoint "Django Admin (via Kong)" "http://localhost:8000/admin/login/" "200"
test_endpoint "Gateway FastAPI (via Kong)" "http://localhost:8000/fast-api/docs" "200"
echo ""

echo "=== Kong Metrics ==="
test_endpoint "Prometheus Metrics" "http://localhost:8001/metrics" "200"
echo ""

echo "=== Rate Limiting Test ==="
echo "Sending 10 requests to /api/cameras/..."
for i in {1..10}; do
    response=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:8000/api/cameras/" 2>/dev/null || echo "000")
    echo -n "$response "
done
echo ""
echo -e "${YELLOW}Note: After 100 requests/min, you should see 429 (Too Many Requests)${NC}"
echo ""

echo "=== Kong Configuration ==="
echo "Checking Kong declarative config..."
docker exec gtvision_kong kong config parse /etc/kong/kong.yml && echo -e "${GREEN}✓ Config valid${NC}" || echo -e "${RED}✗ Config invalid${NC}"
echo ""

echo "=== Kong Status ==="
curl -s http://localhost:8001/status | jq '.' 2>/dev/null || echo "Install jq for formatted output"
echo ""

echo "✅ Kong tests completed!"
echo ""
echo "📊 Access Kong Manager: http://localhost:8002"
echo "📈 Access Metrics: http://localhost:8001/metrics"
echo "📖 Access Admin API: http://localhost:8001"
