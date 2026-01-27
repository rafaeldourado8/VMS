@echo off
setlocal enabledelayedexpansion

set CITY_ID=2ca65fec-ed93-40d1-bdf2-386a94e25fb1
set CAMERA_ID=d7ebdaac-9d09-470f-a208-34ce2e4f9689

echo === PASSO 7 - Teste de Gravacao Ciclica ===
echo.

echo [1] Iniciando stream RTMP...
curl -s -X POST http://localhost:8001/api/streaming/start/%CAMERA_ID% ^
  -H "X-City-ID: %CITY_ID%" ^
  -H "X-User-ID: 1"
echo.
echo.

echo [2] Aguardando 3 segundos...
ping -n 4 127.0.0.1 >nul

echo [3] Habilitando gravacao...
curl -s -X POST http://localhost:8001/api/recording/enable/%CAMERA_ID% ^
  -H "X-City-ID: %CITY_ID%" ^
  -H "X-User-ID: 1"
echo.
echo.

echo [4] Verificando status da gravacao...
curl -s http://localhost:8001/api/recording/status/%CAMERA_ID% ^
  -H "X-City-ID: %CITY_ID%" ^
  -H "X-User-ID: 1"
echo.
echo.

echo [5] Aguardando 60 segundos para gerar arquivo...
ping -n 61 127.0.0.1 >nul

echo [6] Verificando arquivos gravados...
docker exec mediamtx ls -lh /recordings/%CITY_ID%/%CAMERA_ID%/ 2^>^&1
echo.

echo [7] Desabilitando gravacao...
curl -s -X POST http://localhost:8001/api/recording/disable/%CAMERA_ID% ^
  -H "X-City-ID: %CITY_ID%" ^
  -H "X-User-ID: 1"
echo.
echo.

echo === Teste Concluido ===
