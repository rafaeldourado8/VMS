@echo off
REM Teste de Fallback do Streaming
echo ========================================
echo Teste de Fallback - Sistema de Streaming
echo ========================================
echo.

echo [1/5] Verificando cameras no backend...
curl -s http://localhost/api/cameras/for_recorder/ | python -m json.tool
echo.

echo [2/5] Verificando streams no MediaMTX...
curl -s http://localhost:8001/stats | python -m json.tool
echo.

echo [3/5] Simulando restart do backend...
docker restart gtvision_backend
timeout /t 15 /nobreak
echo.

echo [4/5] Aguardando backend voltar...
:wait_backend
curl -s http://localhost/admin/login/ >nul 2>&1
if errorlevel 1 (
    echo Aguardando backend...
    timeout /t 2 /nobreak >nul
    goto wait_backend
)
echo Backend online!
echo.

echo [5/5] Verificando se cameras foram restauradas...
timeout /t 10 /nobreak
curl -s http://localhost:8001/stats | python -m json.tool
echo.

echo ========================================
echo Teste concluido!
echo Verifique se as cameras foram restauradas automaticamente
echo ========================================
