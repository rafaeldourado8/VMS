@echo off
echo Aguardando 20s...
timeout /t 20 /nobreak >nul
echo Publicando camera...
docker-compose exec lpr_service python -c "import redis,json;r=redis.Redis(host='redis_cache',port=6379,db=2);r.publish('camera:provisioned',json.dumps({'camera_id':555,'rtsp_url':'/app/test_video.mp4'}))"
echo Aguardando 30s...
timeout /t 30 /nobreak >nul
echo.
echo === RESULTADOS ===
docker-compose exec lpr_service find /app/snapshots/cam_555 -name "metadata.json" 2>nul | head -5
