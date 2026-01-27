@echo off
set CITY_ID=2ca65fec-ed93-40d1-bdf2-386a94e25fb1
set CAMERA_ID=d7ebdaac-9d09-470f-a208-34ce2e4f9689

echo === PASSO 7 - Gravacao com Stream Ativo ===
echo Camera: RTMP 01
echo.

echo [1] Iniciar stream RTMP...
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

echo [4] Status...
curl -s http://localhost:8001/api/recording/status/%CAMERA_ID% ^
  -H "X-City-ID: %CITY_ID%" ^
  -H "X-User-ID: 1"
echo.
echo.

echo [5] Aguardar 35s para gerar segmento...
ping -n 36 127.0.0.1 >nul

echo [6] Verificar arquivos no host...
dir recordings\%CITY_ID%\%CAMERA_ID% 2^>nul
echo.

echo [7] Desabilitar...
curl -s -X POST http://localhost:8001/api/recording/disable/%CAMERA_ID% ^
  -H "X-City-ID: %CITY_ID%" ^
  -H "X-User-ID: 1"
echo.
