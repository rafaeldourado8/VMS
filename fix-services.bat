@echo off
echo ========================================
echo Corrigindo servicos do GTVision
echo ========================================

echo.
echo [1/4] Parando containers...
docker-compose down

echo.
echo [2/4] Removendo volumes antigos do RabbitMQ...
docker volume rm vms_gtvision_rabbitmq_data 2>nul

echo.
echo [3/4] Reconstruindo e iniciando servicos...
docker-compose up -d --build

echo.
echo [4/4] Aguardando inicializacao (30s)...
timeout /t 30 /nobreak

echo.
echo ========================================
echo Status dos servicos:
echo ========================================
docker-compose ps

echo.
echo ========================================
echo Logs do RabbitMQ:
echo ========================================
docker-compose logs --tail=20 rabbitmq

echo.
echo ========================================
echo Logs do Celery Worker:
echo ========================================
docker-compose logs --tail=20 backend_worker

echo.
echo ========================================
echo Concluido! Acesse:
echo - Frontend: http://localhost
echo - API: http://localhost/api/
echo - RabbitMQ: http://localhost:15672 (user: gtvision_user)
echo ========================================
