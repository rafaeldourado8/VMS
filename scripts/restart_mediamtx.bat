@echo off
echo Reiniciando MediaMTX com configuracao corrigida...

docker-compose restart mediamtx

echo Aguardando inicializacao...
timeout /t 10

echo.
echo Status:
docker logs gtvision_mediamtx --tail 20

pause
