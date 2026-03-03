@echo off
REM Script de Diagnostico - Frontend Connection Refused
REM Verifica status do frontend e HAProxy

echo ========================================
echo DIAGNOSTICO - FRONTEND CONNECTION
echo ========================================
echo.

REM 1. Verificar se container esta rodando
echo [1/5] Verificando container frontend...
docker ps --filter "name=gtvision_frontend" --format "{{.Status}}" | findstr /i "up" >nul
if %errorlevel% equ 0 (
    echo [OK] Container frontend esta rodando
) else (
    echo [ERRO] Container frontend NAO esta rodando
    echo Solucao: docker-compose up -d frontend
    goto :end
)
echo.

REM 2. Verificar healthcheck
echo [2/5] Verificando healthcheck...
docker inspect gtvision_frontend --format "{{.State.Health.Status}}" 2>nul | findstr /i "healthy" >nul
if %errorlevel% equ 0 (
    echo [OK] Frontend healthcheck: healthy
) else (
    docker inspect gtvision_frontend --format "{{.State.Health.Status}}" 2>nul | findstr /i "starting" >nul
    if %errorlevel% equ 0 (
        echo [AVISO] Frontend healthcheck: starting (aguarde 1-2 minutos)
    ) else (
        echo [ERRO] Frontend healthcheck: unhealthy
        echo Verificar logs: docker logs gtvision_frontend
    )
)
echo.

REM 3. Verificar logs recentes
echo [3/5] Verificando logs do frontend (ultimas 10 linhas)...
docker logs gtvision_frontend --tail 10 2>&1 | findstr /i "error err fail" >nul
if %errorlevel% equ 0 (
    echo [AVISO] Erros encontrados nos logs:
    docker logs gtvision_frontend --tail 10 2>&1 | findstr /i "error err fail"
) else (
    echo [OK] Nenhum erro critico nos logs
)
echo.

REM 4. Testar conectividade interna
echo [4/5] Testando conectividade interna (frontend:5173)...
docker exec gtvision_haproxy wget -q --spider http://frontend:5173 2>nul
if %errorlevel% equ 0 (
    echo [OK] HAProxy consegue conectar no frontend
) else (
    echo [ERRO] HAProxy NAO consegue conectar no frontend
    echo Possivel causa: Vite ainda nao iniciou
)
echo.

REM 5. Verificar HAProxy stats
echo [5/5] Verificando status no HAProxy...
curl -s http://localhost:8404/stats 2>nul | findstr /i "frontend_dev.*UP" >nul
if %errorlevel% equ 0 (
    echo [OK] HAProxy marcou frontend como UP
) else (
    echo [AVISO] HAProxy ainda nao marcou frontend como UP
    echo Aguarde 1-2 minutos ou verifique: http://localhost:8404/stats
)
echo.

echo ========================================
echo RESUMO
echo ========================================
echo.
echo Comandos uteis:
echo   docker logs gtvision_frontend -f
echo   docker logs gtvision_haproxy -f
echo   docker-compose restart frontend
echo   http://localhost:8404/stats (admin / GtV!sionHAProxy$2025)
echo.
echo Documentacao: docs/FIX_FRONTEND_CONNECTION_REFUSED.md
echo ========================================

:end
pause
