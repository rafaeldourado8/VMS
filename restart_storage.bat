@echo off
echo Reiniciando Storage Service...

docker-compose stop storage
docker-compose rm -f storage
docker-compose up -d --build storage

echo.
echo Aguardando...
timeout /t 10

echo.
echo Status:
docker logs gtvision_storage --tail 20

pause
