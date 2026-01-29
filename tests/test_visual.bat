@echo off
echo === TESTE COM VISUALIZACAO ===
echo.

echo Aguardando servico (15s)...
timeout /t 15 /nobreak >nul

echo Limpando snapshots...
docker-compose exec lpr_service rm -rf /app/snapshots/*

echo Publicando camera 300...
docker-compose exec lpr_service python -c "import redis,json;r=redis.Redis(host='redis_cache',port=6379,db=2);r.publish('camera:provisioned',json.dumps({'camera_id':300,'rtsp_url':'/app/test_video.mp4'}))"

echo.
echo ========================================
echo STREAM ANOTADO DISPONIVEL EM:
echo   rtsp://localhost:8554/cam_300_ai
echo ========================================
echo.
echo Abra no VLC:
echo   vlc rtsp://localhost:8554/cam_300_ai
echo.
echo Ou FFplay:
echo   ffplay rtsp://localhost:8554/cam_300_ai
echo.
echo Pressione Ctrl+C para sair
echo.

docker-compose logs -f lpr_service
