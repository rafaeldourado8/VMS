@echo off
timeout /t 25 /nobreak >nul
docker-compose exec lpr_service python -c "import redis,json;r=redis.Redis(host='redis_cache',port=6379,db=2);r.publish('camera:provisioned',json.dumps({'camera_id':700,'rtsp_url':'/app/test_video.mp4'}))"
echo.
echo ========================================
echo ABRA NO VLC:
echo   rtsp://localhost:8554/cam_700_ai
echo ========================================
pause
