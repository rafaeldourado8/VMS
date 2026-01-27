@echo off
setlocal enabledelayedexpansion

set CITY_ID=2ca65fec-ed93-40d1-bdf2-386a94e25fb1
set USER_ID=1

echo === Teste Completo - Mosaicos ===
echo.

REM Get camera public IDs
echo Obtendo IDs das cameras...
for /f "tokens=*" %%i in ('docker exec -i django python -c "import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings'); import django; django.setup(); from shared.admin.cameras.models import Camera; cameras = Camera.objects.all()[:4]; [print(c.public_id) for c in cameras]"') do (
    if not defined CAM1 (
        set CAM1=%%i
    ) else if not defined CAM2 (
        set CAM2=%%i
    ) else if not defined CAM3 (
        set CAM3=%%i
    ) else if not defined CAM4 (
        set CAM4=%%i
    )
)

echo Camera 1: %CAM1%
echo Camera 2: %CAM2%
echo Camera 3: %CAM3%
echo Camera 4: %CAM4%
echo.

echo === 1. Iniciando 4 streams ===
echo.

echo Starting stream 1...
curl -X POST http://localhost:8001/api/streaming/start/%CAM1% -H "X-City-ID: %CITY_ID%" -H "X-User-ID: %USER_ID%"
echo.

echo Starting stream 2...
curl -X POST http://localhost:8001/api/streaming/start/%CAM2% -H "X-City-ID: %CITY_ID%" -H "X-User-ID: %USER_ID%"
echo.

echo Starting stream 3...
curl -X POST http://localhost:8001/api/streaming/start/%CAM3% -H "X-City-ID: %CITY_ID%" -H "X-User-ID: %USER_ID%"
echo.

echo Starting stream 4...
curl -X POST http://localhost:8001/api/streaming/start/%CAM4% -H "X-City-ID: %CITY_ID%" -H "X-User-ID: %USER_ID%"
echo.

echo === 2. Listando sessoes ativas ===
curl http://localhost:8001/api/streaming/sessions -H "X-City-ID: %CITY_ID%"
echo.
echo.

echo === 3. Verificando MediaMTX ===
curl http://localhost:9997/v3/paths/list
echo.
echo.

echo === 4. Criando mosaico ===
curl -X POST http://localhost:8001/api/mosaics/create -H "X-City-ID: %CITY_ID%" -H "X-User-ID: %USER_ID%"
echo.
echo.

echo === Teste Completo ===
echo 4 streams iniciados simultaneamente
echo Verifique: http://localhost:9997/v3/paths/list
pause
