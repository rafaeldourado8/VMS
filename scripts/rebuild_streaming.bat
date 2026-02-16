@echo off
echo Reconstruindo Streaming Service...

docker-compose stop streaming mediamtx_monitor
docker-compose rm -f streaming mediamtx_monitor

docker-compose build --no-cache streaming

docker-compose up -d streaming mediamtx_monitor

echo.
echo Aguardando inicializacao...
timeout /t 10

echo.
echo Logs do Streaming:
docker logs gtvision_streaming --tail 30

pause
