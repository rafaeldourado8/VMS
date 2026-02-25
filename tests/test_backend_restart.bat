@echo off
echo ========================================
echo Teste: Restart Backend + Auto-Provision
echo ========================================
echo.

echo [1] Verificando cameras antes do restart...
curl -s http://localhost:8001/stats
echo.
echo.

echo [2] Restartando backend...
docker restart gtvision_backend
echo.

echo [3] Aguardando backend voltar (90s)...
timeout /t 90 /nobreak
echo.

echo [4] Verificando cameras apos restart...
curl -s http://localhost:8001/stats
echo.
echo.

echo [5] Testando acesso HLS da camera 15...
curl -I http://localhost/hls/cam_15/index.m3u8
echo.

echo ========================================
echo Teste concluido!
echo Se ver "200 OK" acima, o fix funcionou!
echo ========================================
