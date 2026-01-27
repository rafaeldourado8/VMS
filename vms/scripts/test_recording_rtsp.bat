@echo off
setlocal enabledelayedexpansion

set CITY_ID=2ca65fec-ed93-40d1-bdf2-386a94e25fb1
set CAMERA_ID=0c4a7f3e-ec5f-4c5e-b5e5-d5e5e5e5e5e5

echo === PASSO 7 - Teste Gravacao RTSP ===
echo.

echo [1] Iniciando stream RTSP...
curl -s -X POST http://localhost:8001/api/streaming/start/%CAMERA_ID% ^
  -H "X-City-ID: %CITY_ID%" ^
  -H "X-User-ID: 1"
echo.
echo.

echo [2] Aguardando 5 segundos...
ping -n 6 127.0.0.1 >nul

echo [3] Habilitando gravacao...
curl -s -X POST http://localhost:8001/api/recording/enable/%CAMERA_ID% ^
  -H "X-City-ID: %CITY_ID%" ^
  -H "X-User-ID: 1"
echo.
echo.

echo [4] Status da gravacao...
curl -s http://localhost:8001/api/recording/status/%CAMERA_ID% ^
  -H "X-City-ID: %CITY_ID%" ^
  -H "X-User-ID: 1"
echo.
echo.

echo [5] Aguardando 60 segundos para gerar arquivo...
ping -n 61 127.0.0.1 >nul

echo [6] Arquivos gravados...
docker exec mediamtx ls -lh /recordings/%CITY_ID%/%CAMERA_ID%/ 2^>^&1
echo.

echo [7] Desabilitando gravacao...
curl -s -X POST http://localhost:8001/api/recording/disable/%CAMERA_ID% ^
  -H "X-City-ID: %CITY_ID%" ^
  -H "X-User-ID: 1"
echo.
