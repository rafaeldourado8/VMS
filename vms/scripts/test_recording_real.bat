@echo off
set CITY_ID=2ca65fec-ed93-40d1-bdf2-386a94e25fb1
set CAMERA_ID=12eb1628-8cb5-42fa-b73c-ec77f00e1a28

echo === PASSO 7 - Gravacao Real (MediaMTX) ===
echo Camera: RTSP 04
echo.

echo [1] Iniciar stream RTSP...
curl -s -X POST http://localhost:8001/api/streaming/start/%CAMERA_ID% ^
  -H "X-City-ID: %CITY_ID%" ^
  -H "X-User-ID: 1"
echo.
echo.

echo [2] Aguardar 5s...
ping -n 6 127.0.0.1 >nul

echo [3] Habilitar gravacao...
curl -s -X POST http://localhost:8001/api/recording/enable/%CAMERA_ID% ^
  -H "X-City-ID: %CITY_ID%" ^
  -H "X-User-ID: 1"
echo.
echo.

echo [4] Status gravacao...
curl -s http://localhost:8001/api/recording/status/%CAMERA_ID% ^
  -H "X-City-ID: %CITY_ID%" ^
  -H "X-User-ID: 1"
echo.
echo.

echo [5] Aguardar 60s para gerar arquivo...
ping -n 61 127.0.0.1 >nul

echo [6] Verificar path MediaMTX...
curl -s http://localhost:9997/v3/paths/get/stream_%CAMERA_ID% | findstr record
echo.
echo.

echo [7] Listar arquivos gravados...
docker exec mediamtx find /recordings/%CITY_ID%/%CAMERA_ID%/ -name "*.mp4" 2^>^&1 ^| head -5
echo.

echo [8] Desabilitar gravacao...
curl -s -X POST http://localhost:8001/api/recording/disable/%CAMERA_ID% ^
  -H "X-City-ID: %CITY_ID%" ^
  -H "X-User-ID: 1"
echo.
