@echo off
echo ========================================
echo TESTE LPR COM OCR
echo ========================================
echo.
echo Aguardando servico iniciar (15s)...
timeout /t 15 /nobreak >nul
echo.
echo Publicando camera 555...
docker-compose exec lpr_service python -c "import redis,json;r=redis.Redis(host='redis_cache',port=6379,db=2);r.publish('camera:provisioned',json.dumps({'camera_id':555,'rtsp_url':'/app/test_video.mp4'}));print('OK')"
echo.
echo Aguardando processamento (30s)...
timeout /t 30 /nobreak
echo.
echo ========================================
echo LOGS
echo ========================================
docker-compose logs --tail=100 lpr_service | findstr /C:"[DETECT]" /C:"[SNAPSHOT]" /C:"Placa:"
echo.
echo ========================================
echo SNAPSHOTS
echo ========================================
docker-compose exec lpr_service find /app/snapshots -name "metadata.json" -exec cat {} \;
