@echo off
echo ========================================
echo Diagnostico Completo do Sistema
echo ========================================

echo.
echo [1] Status dos containers...
docker-compose ps

echo.
echo [2] Logs do Backend (ultimas 30 linhas)...
docker-compose logs --tail=30 backend

echo.
echo [3] Logs do HAProxy (ultimas 20 linhas)...
docker-compose logs --tail=20 haproxy

echo.
echo [4] Logs do Kong (ultimas 20 linhas)...
docker-compose logs --tail=20 kong

echo.
echo [5] Testando conectividade...
echo Backend direto (porta 8000):
curl -s -o nul -w "Status: %%{http_code}\n" http://localhost:8000/admin/login/
echo HAProxy (porta 80):
curl -s -o nul -w "Status: %%{http_code}\n" http://localhost/admin/login/

echo.
echo [6] Healthcheck do backend...
docker-compose exec -T backend curl -f http://localhost:8000/admin/login/ 2>&1 | findstr /i "200 301 302"

echo.
echo ========================================
pause
