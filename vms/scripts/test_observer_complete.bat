@echo off
set CITY_ID=2ca65fec-ed93-40d1-bdf2-386a94e25fb1
set CAMERA_ID=d7ebdaac-9d09-470f-a208-34ce2e4f9689

echo === Path Observer - Teste Completo ===
echo.

echo [1] Registrar stream...
curl -s -X POST http://localhost:8001/api/streaming/start/%CAMERA_ID% ^
  -H "X-City-ID: %CITY_ID%" ^
  -H "X-User-ID: 1"
echo.
echo.

echo [2] Aguardar 15s para observer detectar...
ping -n 16 127.0.0.1 >nul

echo [3] Verificar paths no MediaMTX...
curl -s http://localhost:9997/v3/paths/list | findstr itemCount
echo.
echo.

echo [4] Logs do PathObserver...
docker logs fastapi 2>&1 | findstr /I "PathObserver Path"
echo.
