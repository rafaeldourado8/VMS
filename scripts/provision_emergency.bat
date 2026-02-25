@echo off
REM Script de Emergencia - Provisiona todas as cameras manualmente
echo ========================================
echo EMERGENCIA: Provisionamento Manual
echo ========================================
echo.

echo Copiando script para container...
docker cp provision_now.py gtvision_backend:/app/provision_now.py
echo.

echo Executando provisionamento...
docker exec gtvision_backend python provision_now.py
echo.

echo ========================================
echo Verificando resultado...
echo ========================================
curl -s http://localhost:8001/stats
echo.
echo.

echo ========================================
echo Concluido!
echo ========================================
