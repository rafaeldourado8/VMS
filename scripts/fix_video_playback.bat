@echo off
echo Reiniciando HAProxy para aplicar configuracoes de video...
docker-compose restart haproxy
echo.
echo Aguardando HAProxy...
timeout /t 3 /nobreak >nul
echo.
echo Testando acesso a recordings...
curl -I http://localhost/recordings/
echo.
echo HAProxy reiniciado. Teste o player novamente.
