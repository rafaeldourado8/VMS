@echo off
timeout /t 20 /nobreak >nul
docker-compose exec lpr_service python -c "import redis,json;r=redis.Redis(host='redis_cache',port=6379,db=2);r.publish('camera:provisioned',json.dumps({'camera_id':999,'rtsp_url':'/app/test_video.mp4'}))"
echo Camera 999 publicada. Aguardando 30s...
timeout /t 30 /nobreak >nul
echo.
echo === LOGS OCR ===
docker-compose logs --tail=50 lpr_service | findstr /C:"[OCR]" /C:"[SNAPSHOT]" /C:"Placa:"
echo.
echo === METADATA SAMPLE ===
docker-compose exec lpr_service find /app/snapshots/cam_999 -name "metadata.json" -print -quit -exec cat {} \;
