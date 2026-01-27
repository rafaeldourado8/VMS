@echo off
setlocal enabledelayedexpansion

set CITY_ID=2ca65fec-ed93-40d1-bdf2-386a94e25fb1
set CAMERA_ID=12eb1628-8cb5-42fa-b73c-ec77f00e1a28

echo === PASSO 7 - Gravacao Ciclica RTSP ===
echo Camera: RTSP 04 (rtsp://admin:Camerite123@45.236.226.71:6047)
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

echo [5] Aguardando 60 segundos para gerar segmento...
ping -n 61 127.0.0.1 >nul

echo [6] Verificando arquivos (via find)...
docker exec mediamtx find /recordings/%CITY_ID%/%CAMERA_ID%/ -type f 2^>^&1
echo.

echo [7] Contando arquivos...
docker exec mediamtx sh -c "find /recordings/%CITY_ID%/%CAMERA_ID%/ -type f | wc -l" 2^>^&1
echo.

echo [8] Desabilitando gravacao...
curl -s -X POST http://localhost:8001/api/recording/disable/%CAMERA_ID% ^
  -H "X-City-ID: %CITY_ID%" ^
  -H "X-User-ID: 1"
echo.
echo.

echo === Teste Concluido ===
