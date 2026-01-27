@echo off
set CITY_ID=2ca65fec-ed93-40d1-bdf2-386a94e25fb1
set CAMERA_ID=12eb1628-8cb5-42fa-b73c-ec77f00e1a28

echo === PASSO 7 - Gravacao (Mock) ===
echo.

echo [1] Habilitar gravacao...
curl -s -X POST http://localhost:8001/api/recording/enable/%CAMERA_ID% ^
  -H "X-City-ID: %CITY_ID%" ^
  -H "X-User-ID: 1"
echo.
echo.

echo [2] Status...
curl -s http://localhost:8001/api/recording/status/%CAMERA_ID% ^
  -H "X-City-ID: %CITY_ID%" ^
  -H "X-User-ID: 1"
echo.
echo.

echo [3] Desabilitar gravacao...
curl -s -X POST http://localhost:8001/api/recording/disable/%CAMERA_ID% ^
  -H "X-City-ID: %CITY_ID%" ^
  -H "X-User-ID: 1"
echo.
echo.

echo [4] Status apos desabilitar...
curl -s http://localhost:8001/api/recording/status/%CAMERA_ID% ^
  -H "X-City-ID: %CITY_ID%" ^
  -H "X-User-ID: 1"
echo.
