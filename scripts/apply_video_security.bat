@echo off
echo ========================================
echo FIX: Video Playback (Auth Desabilitado)
echo ========================================
echo.

echo [1/2] Reiniciando Nginx...
docker-compose restart nginx
timeout /t 2 /nobreak >nul

echo [2/2] Reiniciando HAProxy...
docker-compose restart haproxy
timeout /t 2 /nobreak >nul

echo.
echo ========================================
echo STATUS:
echo ========================================
echo [OK] Video playback restaurado
echo [WARN] Recordings sem autenticacao (TODO)
echo.
echo PROXIMOS PASSOS:
echo 1. Ver docs\SECURITY_RECORDINGS_TODO.md
echo 2. Implementar proxy via Django
echo 3. Adicionar permissoes por camera
echo.
echo Recarregue o frontend (Ctrl+Shift+R)
echo.
pause
