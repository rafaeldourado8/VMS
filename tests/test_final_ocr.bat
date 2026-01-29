@echo off
echo Aguardando 20s para servico iniciar...
timeout /t 20 /nobreak >nul
echo Publicando camera 888...
docker-compose exec lpr_service python -c "import redis,json;r=redis.Redis(host='redis_cache',port=6379,db=2);r.publish('camera:provisioned',json.dumps({'camera_id':888,'rtsp_url':'/app/test_video.mp4'}))"
echo Aguardando 30s para processar...
timeout /t 30 /nobreak >nul
echo.
echo === VERIFICANDO RESULTADOS ===
docker-compose exec lpr_service find /app/snapshots/cam_888 -name "metadata.json" -print -exec cat {} \; 2>nul | findstr /C:"plate_text" /C:"License_Plate"
