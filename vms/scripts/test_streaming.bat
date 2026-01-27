@echo off
echo === Teste de Streaming ===
echo.

set CITY_ID=2ca65fec-ed93-40d1-bdf2-386a94e25fb1
set CAMERA_PUBLIC_ID=8392ef0c-eac9-4dfc-a38a-e4cf4a114517

echo 1. Starting stream...
curl -X POST http://localhost:8001/api/streaming/start/%CAMERA_PUBLIC_ID% ^
  -H "X-City-ID: %CITY_ID%" ^
  -H "X-User-ID: 1"

echo.
echo.
echo 2. Listing active sessions...
curl http://localhost:8001/api/streaming/sessions ^
  -H "X-City-ID: %CITY_ID%"

echo.
echo.
echo 3. Check MediaMTX paths...
curl http://localhost:9997/v3/paths/list

echo.
echo.
echo === Teste Completo ===
echo Abra: http://localhost
echo Digite o session_id retornado acima
pause
