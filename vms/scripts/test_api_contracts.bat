@echo off
set CITY_ID=2ca65fec-ed93-40d1-bdf2-386a94e25fb1
set CAMERA_ID=d7ebdaac-9d09-470f-a208-34ce2e4f9689

echo === Testando Novos Contratos API ===
echo.

echo [1] Health Check...
curl -s http://localhost:8001/health
echo.
echo.

echo [2] POST /api/v1/streams (Iniciar stream)...
curl -s -X POST "http://localhost:8001/api/v1/streams?camera_id=%CAMERA_ID%" ^
  -H "X-City-ID: %CITY_ID%" ^
  -H "X-User-ID: 1"
echo.
echo.

echo [3] GET /api/v1/streams (Listar streams)...
curl -s http://localhost:8001/api/v1/streams ^
  -H "X-City-ID: %CITY_ID%"
echo.
echo.

echo [4] PUT /api/v1/cameras/{id}/recording (Habilitar gravacao)...
curl -s -X PUT http://localhost:8001/api/v1/cameras/%CAMERA_ID%/recording ^
  -H "X-City-ID: %CITY_ID%" ^
  -H "X-User-ID: 1"
echo.
echo.

echo [5] GET /api/v1/cameras/{id}/recording (Status gravacao)...
curl -s http://localhost:8001/api/v1/cameras/%CAMERA_ID%/recording ^
  -H "X-City-ID: %CITY_ID%" ^
  -H "X-User-ID: 1"
echo.
echo.

echo [6] Documentacao: http://localhost:8001/docs
