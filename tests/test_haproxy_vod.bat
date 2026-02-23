@echo off
echo ========================================
echo Testando HAProxy - VOD Routing
echo ========================================
echo.

echo [1/4] Testando VOD Service direto (porta 8006)...
curl -s http://localhost:8006/health
echo.
echo.

echo [2/4] Testando VOD via HAProxy (porta 80)...
curl -s http://localhost/vod/health 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERRO: Rota /vod/ nao esta funcionando via HAProxy
) else (
    echo OK: Rota /vod/ funcionando!
)
echo.
echo.

echo [3/4] Testando playlist HLS via HAProxy...
echo Exemplo: http://localhost/vod/camera_1/2026-02-20/12-44-27.mp4/index.m3u8
echo (Substitua com um arquivo real)
echo.

echo [4/4] Verificando HAProxy Stats...
echo Acesse: http://localhost:8404/stats
echo.

echo ========================================
echo Teste concluido!
echo ========================================
echo.
echo Proximos passos:
echo 1. Verifique se vod_hls container esta rodando: docker ps
echo 2. Teste com arquivo real de gravacao
echo 3. Integre no frontend
echo.
pause
