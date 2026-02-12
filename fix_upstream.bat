@echo off
echo Verificando status dos servicos...

docker ps --filter "name=gtvision" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo.
echo Verificando logs do HAProxy...
docker logs gtvision_haproxy --tail 50

echo.
echo Verificando logs do Kong...
docker logs gtvision_kong --tail 50

echo.
echo Verificando logs do Backend...
docker logs gtvision_backend --tail 50

echo.
echo Testando conectividade interna...
docker exec gtvision_haproxy wget -O- http://kong:8000/api/health 2>&1
docker exec gtvision_haproxy wget -O- http://backend:8000/admin/login/ 2>&1

pause
