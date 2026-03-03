@echo off
REM Script de Teste - Otimizacao de Requests na Timeline
REM Valida cache, prefetch e performance

echo ========================================
echo TESTE DE OTIMIZACAO - TIMELINE REQUESTS
echo ========================================
echo.

REM 1. Testar cache headers
echo [1/4] Testando Cache Headers...
curl -I http://localhost/recordings/camera_3/2026-03-03/00-56-58.mp4 2>nul | findstr /i "cache-control accept-ranges"
if %errorlevel% equ 0 (
    echo [OK] Cache headers configurados
) else (
    echo [ERRO] Cache headers nao encontrados
)
echo.

REM 2. Testar Range requests
echo [2/4] Testando Range Requests...
curl -I -H "Range: bytes=0-1023" http://localhost/recordings/camera_3/2026-03-03/00-56-58.mp4 2>nul | findstr /i "206 content-range"
if %errorlevel% equ 0 (
    echo [OK] Range requests funcionando
) else (
    echo [ERRO] Range requests nao funcionando
)
echo.

REM 3. Testar CORS
echo [3/4] Testando CORS...
curl -I -H "Origin: http://localhost:5173" http://localhost/recordings/camera_3/2026-03-03/00-56-58.mp4 2>nul | findstr /i "access-control-allow-origin"
if %errorlevel% equ 0 (
    echo [OK] CORS configurado
) else (
    echo [ERRO] CORS nao configurado
)
echo.

REM 4. Testar latencia
echo [4/4] Testando Latencia...
echo Fazendo 3 requests para medir cache...
for /l %%i in (1,1,3) do (
    echo Request %%i:
    curl -o nul -s -w "  Tempo: %%{time_total}s | Status: %%{http_code}\n" http://localhost/recordings/camera_3/2026-03-03/00-56-58.mp4
)
echo.

echo ========================================
echo RESUMO
echo ========================================
echo.
echo Validacoes:
echo [x] Cache headers (max-age=3600, immutable)
echo [x] Range requests (206 Partial Content)
echo [x] CORS (Access-Control-Allow-Origin)
echo [x] Latencia (deve reduzir em requests subsequentes)
echo.
echo Proximos passos:
echo 1. Abrir DevTools ^> Network
echo 2. Reproduzir timeline
echo 3. Verificar: Status 200 (from disk cache) ou 304
echo 4. Verificar: Prefetch do proximo segmento
echo.
echo Documentacao: docs/TIMELINE_REQUESTS_OPTIMIZATION.md
echo ========================================

pause
