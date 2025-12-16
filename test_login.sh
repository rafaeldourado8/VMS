#!/bin/bash
# Script de teste do login

echo "🧪 Testando Login Público..."
echo ""

# Teste 1: Login sem token (deve funcionar)
echo "1️⃣ POST /api/auth/login/ (sem token)"
curl -X POST http://localhost/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  -w "\nHTTP Status: %{http_code}\n" \
  -s | jq .

echo ""
echo "---"
echo ""

# Teste 2: Acessar /me sem token (deve falhar 401)
echo "2️⃣ GET /api/auth/me/ (sem token - deve retornar 401)"
curl -X GET http://localhost/api/auth/me/ \
  -w "\nHTTP Status: %{http_code}\n" \
  -s | jq .

echo ""
echo "---"
echo ""

# Teste 3: Login e depois acessar /me com token
echo "3️⃣ Fluxo completo: Login → Acessar /me"
TOKEN=$(curl -X POST http://localhost/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  -s | jq -r .access)

echo "Token obtido: ${TOKEN:0:50}..."
echo ""

curl -X GET http://localhost/api/auth/me/ \
  -H "Authorization: Bearer $TOKEN" \
  -w "\nHTTP Status: %{http_code}\n" \
  -s | jq .

echo ""
echo "✅ Testes concluídos!"
