@echo off
echo === Adicionando cameras via API MediaMTX ===
echo.

curl -X POST http://localhost:9997/v3/config/paths/add/camera_rtsp -H "Content-Type: application/json" -d "{\"source\":\"rtsp://admin:Camerite123@45.236.226.71:6047/cam/realmonitor?channel=1^&subtype=0\",\"sourceOnDemand\":false}"

echo.

curl -X POST http://localhost:9997/v3/config/paths/add/camera_rtmp -H "Content-Type: application/json" -d "{\"source\":\"rtmp://inst-t4ntf-srs-rtmp-intelbras.camerite.services:1935/record/7KOM2715717FV.stream\",\"sourceOnDemand\":false}"

echo.

curl -X POST http://localhost:9997/v3/config/paths/add/camera_ip -H "Content-Type: application/json" -d "{\"source\":\"rtsp://138.255.75.231:503\",\"sourceOnDemand\":false}"

echo.
echo === Cameras adicionadas ===
echo Acesse: http://localhost
pause
