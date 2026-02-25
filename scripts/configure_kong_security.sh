#!/bin/bash
# Configuração de Segurança do Kong

KONG_ADMIN="http://localhost:8001"

echo "🔧 Configurando Kong Gateway..."

# 1. Criar serviço para o Backend Django
curl -i -X POST $KONG_ADMIN/services \
  --data name=backend-api \
  --data url=http://backend:8000

# 2. Criar rota para /api/
curl -i -X POST $KONG_ADMIN/services/backend-api/routes \
  --data paths[]=/api \
  --data strip_path=false

# 3. Criar rota para /admin/
curl -i -X POST $KONG_ADMIN/services/backend-api/routes \
  --data paths[]=/admin \
  --data strip_path=false

echo ""
echo "🛡️ Aplicando plugins de segurança..."

# 4. CORS - Permitir requisições do frontend
curl -i -X POST $KONG_ADMIN/services/backend-api/plugins \
  --data name=cors \
  --data config.origins=* \
  --data config.methods=GET,POST,PUT,PATCH,DELETE,OPTIONS \
  --data config.headers=Accept,Authorization,Content-Type,X-Requested-With \
  --data config.exposed_headers=X-Auth-Token \
  --data config.credentials=true \
  --data config.max_age=3600

# 5. Rate Limiting - 1000 req/min por IP
curl -i -X POST $KONG_ADMIN/services/backend-api/plugins \
  --data name=rate-limiting \
  --data config.minute=1000 \
  --data config.policy=local

# 6. Request Size Limiting - Máximo 10MB
curl -i -X POST $KONG_ADMIN/services/backend-api/plugins \
  --data name=request-size-limiting \
  --data config.allowed_payload_size=10

# 7. IP Restriction (opcional - comentado)
# curl -i -X POST $KONG_ADMIN/services/backend-api/plugins \
#   --data name=ip-restriction \
#   --data config.allow=192.168.0.0/16,10.0.0.0/8

# 8. Bot Detection
curl -i -X POST $KONG_ADMIN/services/backend-api/plugins \
  --data name=bot-detection \
  --data config.allow='["googlebot","bingbot"]' \
  --data config.deny='["curl","wget"]'

# 9. Request Transformer - Adicionar headers de segurança
curl -i -X POST $KONG_ADMIN/services/backend-api/plugins \
  --data name=request-transformer \
  --data config.add.headers=X-Forwarded-Proto:https

# 10. Response Transformer - Headers de segurança
curl -i -X POST $KONG_ADMIN/services/backend-api/plugins \
  --data name=response-transformer \
  --data config.add.headers=X-Content-Type-Options:nosniff \
  --data config.add.headers=X-Frame-Options:DENY \
  --data config.add.headers=X-XSS-Protection:1;mode=block

echo ""
echo "✅ Kong configurado com sucesso!"
echo "📊 Acesse: http://localhost:8001 (Admin API)"
echo "🔒 Plugins ativos:"
echo "  - CORS"
echo "  - Rate Limiting (1000 req/min)"
echo "  - Request Size Limiting (10MB)"
echo "  - Bot Detection"
echo "  - Security Headers"
