@echo off
echo Reiniciando clips_worker...
docker-compose stop clips_worker
docker-compose rm -f clips_worker
docker-compose up -d clips_worker
echo.
echo Aguardando inicializacao...
timeout /t 5 /nobreak >nul
echo.
echo Verificando logs...
docker-compose logs --tail=50 clips_worker
