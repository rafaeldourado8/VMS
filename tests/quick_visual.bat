@echo off
timeout /t 20 /nobreak >nul
docker-compose exec lpr_service python -c "import redis,json;r=redis.Redis(host='redis_cache',port=6379,db=2);r.publish('camera:provisioned',json.dumps({'camera_id':400,'rtsp_url':'/app/test_video.mp4'}))"
echo.
echo Stream disponivel em: rtsp://localhost:8554/cam_400_ai
echo Abra no VLC ou aguarde 10s para ver logs...
timeout /t 10 /nobreak >nul
docker-compose logs --tail=50 lpr_service
