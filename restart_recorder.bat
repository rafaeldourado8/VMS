@echo off
echo Reiniciando Recorder...

docker-compose stop recorder
docker-compose rm -f recorder
docker-compose up -d --build recorder

echo.
echo Aguardando...
timeout /t 5

echo.
echo Logs:
docker logs gtvision_recorder --tail 20

pause
