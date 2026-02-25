@echo off
REM Configuração de Segurança do Kong

set KONG_ADMIN=http://localhost:8001

echo Configurando Kong Gateway...

REM 1. Criar serviço para o Backend Django
curl -i -X POST %KONG_ADMIN%/services --data name=backend-api --data url=http://backend:8000

REM 2. Criar rota para /api/
curl -i -X POST %KONG_ADMIN%/services/backend-api/routes --data paths[]=/api --data strip_path=false

REM 3. Criar rota para /admin/
curl -i -X POST %KONG_ADMIN%/services/backend-api/routes --data paths[]=/admin --data strip_path=false

echo.
echo Aplicando plugins de seguranca...

REM 4. CORS
curl -i -X POST %KONG_ADMIN%/services/backend-api/plugins --data name=cors --data config.origins=* --data config.methods=GET,POST,PUT,PATCH,DELETE,OPTIONS --data config.headers=Accept,Authorization,Content-Type,X-Requested-With --data config.credentials=true

REM 5. Rate Limiting - 1000 req/min
curl -i -X POST %KONG_ADMIN%/services/backend-api/plugins --data name=rate-limiting --data config.minute=1000 --data config.policy=local

REM 6. Request Size Limiting - 10MB
curl -i -X POST %KONG_ADMIN%/services/backend-api/plugins --data name=request-size-limiting --data config.allowed_payload_size=10

REM 7. Response Headers de Seguranca
curl -i -X POST %KONG_ADMIN%/services/backend-api/plugins --data name=response-transformer --data "config.add.headers=X-Content-Type-Options:nosniff" --data "config.add.headers=X-Frame-Options:DENY"

echo.
echo Kong configurado com sucesso!
echo Acesse: http://localhost:8001 (Admin API)
pause
