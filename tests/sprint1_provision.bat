@echo off
echo Provisionando camera 999...
echo.

curl -X POST http://localhost:8001/cameras/provision ^
  -H "Content-Type: application/json" ^
  -d "{\"camera_id\": 999, \"rtsp_url\": \"rtsp://admin:admin@192.168.1.100:554/stream1\", \"name\": \"Teste Sprint 1\", \"enabled\": true, \"on_demand\": false}"

echo.
echo.
echo Verificando se foi criada...
timeout /t 3 /nobreak >nul

curl -u mediamtx_api_user:GtV!sionMed1aMTX$2025 http://localhost:9997/v3/paths/get/cam_999

echo.
pause
