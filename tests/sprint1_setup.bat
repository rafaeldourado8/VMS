@echo off
echo ============================================================
echo SPRINT 1 - SETUP COMPLETO
echo ============================================================
echo.

echo [1/3] Iniciando stream de teste em background...
start /B ffmpeg -re -stream_loop -1 -i 1280_720_60fps.mp4 -c copy -f rtsp rtsp://localhost:8554/cam_999 2>nul

echo Aguardando 5 segundos...
timeout /t 5 /nobreak >nul
echo.

echo [2/3] Verificando se MediaMTX recebeu o stream...
curl -s -u mediamtx_api_user:GtV!sionMed1aMTX$2025 http://localhost:9997/v3/paths/get/cam_999
echo.
echo.

echo [3/3] Verificando gravacoes...
timeout /t 3 /nobreak >nul
docker exec gtvision_mediamtx ls -lh /recordings/cam_999/
echo.

echo ============================================================
echo Setup concluido! Aguarde 1 hora para validar gravacoes.
echo Para parar o stream: taskkill /IM ffmpeg.exe /F
echo ============================================================
pause
