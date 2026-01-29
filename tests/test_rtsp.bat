@echo off
echo Aguardando 20s...
timeout /t 20 /nobreak >nul

echo Publicando camera 600...
docker-compose exec lpr_service python -c "import redis,json;r=redis.Redis(host='redis_cache',port=6379,db=2);r.publish('camera:provisioned',json.dumps({'camera_id':600,'rtsp_url':'/app/test_video.mp4'}))"

echo.
echo Aguardando 10s para stream iniciar...
timeout /t 10 /nobreak >nul

echo.
echo ========================================
echo STREAM RTSP DISPONIVEL:
echo   rtsp://localhost:8554/cam_600_ai
echo ========================================
echo.
echo Testando com FFplay...
ffplay -rtsp_transport tcp rtsp://localhost:8554/cam_600_ai
