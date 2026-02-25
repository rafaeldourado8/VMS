@echo off
echo ========================================
echo REBUILD - Auto Provision
echo ========================================
echo.

echo Parando backend...
docker-compose stop backend
docker-compose rm -f backend

echo Rebuild backend...
docker-compose build backend

echo Iniciando backend...
docker-compose up -d backend

echo Aguardando 60s...
timeout /t 60 /nobreak

echo.
echo Logs:
docker logs gtvision_backend --tail 30

echo.
echo Cameras:
curl -s http://localhost:8001/stats

echo.
echo CONCLUIDO!
