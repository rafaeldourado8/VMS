#!/bin/bash
# Script para aguardar todos os serviços estarem prontos

echo "========================================"
echo "Aguardando serviços ficarem prontos..."
echo "========================================"

MAX_WAIT=180
ELAPSED=0

check_service() {
    local service=$1
    local url=$2
    docker exec gtvision_haproxy wget -q -O - "$url" >/dev/null 2>&1
    return $?
}

while [ $ELAPSED -lt $MAX_WAIT ]; do
    # Verificar Kong
    if ! check_service "kong" "http://kong:8000/"; then
        echo "[${ELAPSED}s] Kong ainda não está pronto..."
        sleep 5
        ELAPSED=$((ELAPSED + 5))
        continue
    fi

    # Verificar Frontend
    if ! check_service "frontend" "http://frontend:5173/"; then
        echo "[${ELAPSED}s] Frontend ainda não está pronto..."
        sleep 5
        ELAPSED=$((ELAPSED + 5))
        continue
    fi

    # Verificar Streaming
    if ! check_service "streaming" "http://streaming:8001/health"; then
        echo "[${ELAPSED}s] Streaming ainda não está pronto..."
        sleep 5
        ELAPSED=$((ELAPSED + 5))
        continue
    fi

    # Todos os serviços estão prontos
    echo ""
    echo "========================================"
    echo "[OK] Todos os serviços estão prontos!"
    echo "========================================"
    echo ""
    echo "Acesse: http://localhost/"
    echo "HAProxy Stats: http://localhost:8404/stats"
    echo ""
    exit 0
done

echo "[ERRO] Timeout aguardando serviços (${MAX_WAIT}s)"
exit 1
