@echo off
echo ========================================
echo SECURITY: Recordings com JWT
echo ========================================
echo.

echo [1/3] Reiniciando Backend (novo endpoint)...
docker-compose restart backend
timeout /t 5 /nobreak >nul

echo [2/3] Reiniciando Nginx (proxy config)...
docker-compose restart nginx
timeout /t 2 /nobreak >nul

echo [3/3] Reiniciando HAProxy...
docker-compose restart haproxy
timeout /t 2 /nobreak >nul

echo.
echo ========================================
echo IMPLEMENTACAO COMPLETA:
echo ========================================
echo [OK] Django: /api/recordings/serve/
echo [OK] JWT: @permission_classes([IsAuthenticated])
echo [OK] Nginx: Proxy para Django
echo [OK] Frontend: fetch() com Authorization header
echo [OK] Blob URL para <video> tag
echo.
echo TESTE (deve retornar 401 sem token):
echo curl http://localhost/recordings/camera_1/2026-02-26/08-45-05.mp4
echo.
echo TESTE (deve retornar 200 com token):
echo curl -H "Authorization: Bearer TOKEN" http://localhost/recordings/camera_1/2026-02-26/08-45-05.mp4
echo.
echo Recarregue o frontend (Ctrl+Shift+R)
echo.
pause
