@echo off
cls
echo ========================================
echo   LPR LIVE PREVIEW NO NAVEGADOR
echo ========================================
echo.

echo [1/3] Reiniciando servico...
docker-compose restart lpr_service
timeout /t 20 /nobreak >nul

echo [2/3] Publicando camera 700...
docker-compose exec lpr_service python -c "import redis,json;r=redis.Redis(host='redis_cache',port=6379,db=2);r.publish('camera:provisioned',json.dumps({'camera_id':700,'rtsp_url':'/app/test_video.mp4'}))"

echo [3/3] Aguardando processamento (5s)...
timeout /t 5 /nobreak >nul

echo.
echo ========================================
echo   ABRINDO NAVEGADOR...
echo ========================================
echo.

start "" "d:\vms system\lpr_live.html"

echo Preview atualiza automaticamente a cada 1 segundo!
echo Pressione qualquer tecla para sair...
pause >nul
