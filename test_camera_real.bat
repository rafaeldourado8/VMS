@echo off
echo Testando camera real...

set RTSP_URL=rtsp://admin:Camerite123@45.236.226.72:6049/cam/realmonitor?channel=1^&subtype=0

echo.
echo 1. Crie a camera no frontend com essa URL:
echo %RTSP_URL%
echo.
echo 2. Anote o ID da camera criada
echo.
set /p CAMERA_ID="Digite o ID da camera: "

echo.
echo Iniciando IA para camera %CAMERA_ID%...
curl -X POST http://localhost:5000/cameras/%CAMERA_ID%/start -H "Content-Type: application/json" -d "{}"

echo.
echo.
echo Pronto! Monitore:
echo docker-compose logs -f ai_detection
echo.
echo Recortes em: d:\VMS\detections\
pause
