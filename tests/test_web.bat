@echo off
cls
echo ========================================
echo   TESTE LPR COM VISUALIZACAO WEB
echo ========================================
echo.

echo [1/3] Aguardando servico (20s)...
timeout /t 20 /nobreak >nul

echo [2/3] Publicando camera 700...
docker-compose exec lpr_service python -c "import redis,json;r=redis.Redis(host='redis_cache',port=6379,db=2);r.publish('camera:provisioned',json.dumps({'camera_id':700,'rtsp_url':'/app/test_video.mp4'}))"

echo [3/3] Aguardando stream iniciar (10s)...
timeout /t 10 /nobreak >nul

echo.
echo ========================================
echo   ABRINDO NAVEGADOR...
echo ========================================
echo.

start "" "d:\vms system\lpr_viewer.html"

echo.
echo Stream HLS disponivel em:
echo   http://localhost:8888/cam_700_ai
echo.
echo Pressione qualquer tecla para ver logs...
pause >nul

docker-compose logs --tail=30 lpr_service
