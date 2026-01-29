@echo off
echo Publicando cameras de teste...
docker-compose exec -T lpr_service python -c "import redis,json,time;r=redis.Redis(host='redis_cache',port=6379,db=2);r.ping();print('Redis OK');c1={'camera_id':555,'rtsp_url':'/app/test_video.mp4'};r.publish('camera:provisioned',json.dumps(c1));print('Camera 555 publicada');time.sleep(2);c2={'camera_id':999,'rtsp_url':'rtsp://mediamtx:8554/test_video'};r.publish('camera:provisioned',json.dumps(c2));print('Camera 999 publicada')"
echo.
echo Aguarde 15 segundos para processamento...
timeout /t 15 /nobreak
echo.
echo === LOGS DO LPR ===
docker-compose logs --tail=30 lpr_service
echo.
echo === SNAPSHOTS ===
docker-compose exec lpr_service find /app/snapshots -name "*.json" -exec echo {} \; -exec cat {} \; 2>nul
