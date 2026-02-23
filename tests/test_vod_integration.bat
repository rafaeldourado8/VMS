@echo off
echo ========================================
echo Testando Integracao Backend - VOD HLS
echo ========================================
echo.

echo [1/3] Testando health do VOD Service...
curl -s http://localhost:8006/health
echo.
echo.

echo [2/3] Listando gravacoes via Backend API...
curl -s "http://localhost/api/recordings/?camera_id=1" | python -m json.tool
echo.
echo.

echo [3/3] Testando endpoint HLS de uma gravacao...
echo (Substitua {id} pelo ID de uma gravacao real)
echo curl http://localhost/api/recordings/{id}/hls/
echo.

echo ========================================
echo Teste concluido!
echo ========================================
pause
