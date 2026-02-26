@echo off
echo ========================================
echo SECURITY FIX: Recordings via Django
echo ========================================
echo.

echo [1/3] Reiniciando Backend...
docker-compose restart backend
timeout /t 5 /nobreak >nul

echo [2/3] Reiniciando Nginx...
docker-compose restart nginx
timeout /t 2 /nobreak >nul

echo [3/3] Reiniciando HAProxy...
docker-compose restart haproxy
timeout /t 2 /nobreak >nul

echo.
echo ========================================
echo SECURITY IMPLEMENTADA:
echo ========================================
echo [OK] Recordings agora requerem JWT
echo [OK] Endpoint: /api/recordings/serve/
echo [OK] Nginx proxy para Django
echo [OK] Suporte a Range requests
echo.
echo TESTE:
echo curl -H "Authorization: Bearer TOKEN" http://localhost/recordings/camera_1/2026-02-26/08-45-05.mp4
echo.
echo Recarregue o frontend (Ctrl+Shift+R)
echo.
pause
