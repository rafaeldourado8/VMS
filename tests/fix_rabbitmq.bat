@echo off
echo ========================================
echo Corrigindo RabbitMQ
echo ========================================
echo.

echo [1/3] Parando RabbitMQ...
docker-compose stop rabbitmq
timeout /t 2 >nul

echo.
echo [2/3] Removendo container e volume antigo...
docker-compose rm -f rabbitmq
docker volume rm vms_rabbitmq_data 2>nul
timeout /t 2 >nul

echo.
echo [3/3] Recriando RabbitMQ com volume persistente...
docker-compose up -d rabbitmq
timeout /t 5 >nul

echo.
echo ========================================
echo RabbitMQ corrigido!
echo ========================================
echo.
echo Aguardando inicialização...
timeout /t 10 >nul

docker-compose logs --tail=20 rabbitmq

echo.
pause
