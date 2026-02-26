@echo off
echo ========================================
echo FIX COMPLETO: Video Playback
echo ========================================
echo.

echo [1/4] Reiniciando Nginx...
docker-compose restart nginx
timeout /t 2 /nobreak >nul

echo [2/4] Reiniciando HAProxy...
docker-compose restart haproxy
timeout /t 2 /nobreak >nul

echo [3/4] Testando acesso ao video...
curl -I "http://localhost/recordings/camera_1/2026-02-26/08-45-05.mp4" 2>&1 | findstr "HTTP Content-Type Accept-Ranges"

echo.
echo [4/4] Verificando servicos...
docker-compose ps nginx haproxy

echo.
echo ========================================
echo CORRECOES APLICADAS:
echo ========================================
echo 1. CanvasTimeline: onWheelCapture (fix passive listener)
echo 2. TimelinePlayerModal: logs detalhados
echo 3. Nginx: default_type video/mp4
echo 4. HAProxy: CORS + timeout 300s
echo.
echo Recarregue o frontend (Ctrl+Shift+R)
echo.
pause
