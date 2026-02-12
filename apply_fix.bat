@echo off
echo Aplicando correcoes...

echo Parando servicos afetados...
docker-compose stop haproxy kong backend

echo Removendo containers...
docker-compose rm -f haproxy kong backend

echo Recriando servicos...
docker-compose up -d postgres_db redis_cache
timeout /t 10

docker-compose up -d backend
timeout /t 30

docker-compose up -d kong
timeout /t 10

docker-compose up -d haproxy

echo.
echo Aguardando inicializacao...
timeout /t 20

echo.
echo Status dos servicos:
docker ps --filter "name=gtvision" --format "table {{.Names}}\t{{.Status}}"

echo.
echo Testando endpoints:
curl -I http://localhost/api/
curl -I http://localhost/admin/

pause
