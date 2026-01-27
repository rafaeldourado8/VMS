@echo off
set CITY_ID=2ca65fec-ed93-40d1-bdf2-386a94e25fb1
set CAMERA_ID=d7ebdaac-9d09-470f-a208-34ce2e4f9689

echo === PASSO 7 - Gravacao Automatica ===
echo.

echo [1] Habilitar recording na camera...
curl -s -X POST http://localhost:8001/api/recording/enable/%CAMERA_ID% ^
  -H "X-City-ID: %CITY_ID%" ^
  -H "X-User-ID: 1"
echo.
echo.

echo [2] Iniciar stream (deve gravar automaticamente)...
curl -s -X POST http://localhost:8001/api/streaming/start/%CAMERA_ID% ^
  -H "X-City-ID: %CITY_ID%" ^
  -H "X-User-ID: 1"
echo.
echo.

echo [3] Aguardar 35s para gerar segmento...
ping -n 36 127.0.0.1 >nul

echo [4] Verificar path MediaMTX...
curl -s http://localhost:9997/v3/paths/get/stream_%CAMERA_ID%
echo.
echo.

echo [5] Verificar arquivos...
dir recordings\%CITY_ID%\%CAMERA_ID% 2^>nul
echo.

echo [6] Parar stream...
curl -s -X POST http://localhost:8001/api/streaming/stop/stream_%CAMERA_ID% ^
  -H "X-City-ID: %CITY_ID%"
echo.
