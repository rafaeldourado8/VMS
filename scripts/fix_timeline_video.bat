@echo off
echo ========================================
echo FIX: Timeline Video Playback
echo ========================================
echo.

echo [1/3] Reiniciando Nginx...
docker-compose restart nginx
timeout /t 2 /nobreak >nul

echo [2/3] Reiniciando HAProxy...
docker-compose restart haproxy
timeout /t 3 /nobreak >nul

echo [3/3] Verificando servicos...
docker-compose ps nginx haproxy

echo.
echo ========================================
echo Teste agora o Timeline Player
echo ========================================
echo.
echo Se ainda houver erro, verifique:
echo 1. Se existem arquivos em d:\VMS\recordings\camera_X\
echo 2. Os logs: docker-compose logs nginx haproxy
echo.
pause
