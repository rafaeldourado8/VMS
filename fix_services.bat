@echo off
echo ========================================
echo Reiniciando VMS com correções
echo ========================================

echo Parando serviços com falha...
docker-compose stop ai_worker_1 ai_worker_2 mediamtx rabbitmq

echo Removendo containers com falha...
docker-compose rm -f ai_worker_1 ai_worker_2 mediamtx rabbitmq

echo Reconstruindo AI workers...
docker-compose build ai_worker_1 ai_worker_2

echo Iniciando serviços corrigidos...
docker-compose up -d rabbitmq
timeout /t 10
docker-compose up -d mediamtx
timeout /t 5
docker-compose up -d ai_worker_1 ai_worker_2

echo ========================================
echo Verificando status dos serviços...
echo ========================================
docker-compose ps

echo ========================================
echo Logs dos serviços (últimas 20 linhas)
echo ========================================
echo --- MediaMTX ---
docker-compose logs --tail=20 mediamtx

echo --- RabbitMQ ---
docker-compose logs --tail=20 rabbitmq

echo --- AI Worker 1 ---
docker-compose logs --tail=20 ai_worker_1

echo --- AI Worker 2 ---
docker-compose logs --tail=20 ai_worker_2

echo ========================================
echo Reinicialização concluída!
echo ========================================