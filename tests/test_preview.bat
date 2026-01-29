@echo off
echo === VISUALIZACAO COM PREVIEW ===
echo.
timeout /t 15 /nobreak >nul

echo Limpando...
docker-compose exec lpr_service rm -rf /app/snapshots/*

echo Publicando camera 500...
docker-compose exec lpr_service python -c "import redis,json;r=redis.Redis(host='redis_cache',port=6379,db=2);r.publish('camera:provisioned',json.dumps({'camera_id':500,'rtsp_url':'/app/test_video.mp4'}))"

echo.
echo Processando... Aguarde 30s
timeout /t 30 /nobreak >nul

echo.
echo === PREVIEW SALVO EM ===
echo snapshots\preview\cam_500_preview.jpg
echo.
echo Abrindo preview...
start "" "d:\vms system\snapshots\preview\cam_500_preview.jpg"

echo.
echo === SNAPSHOTS ===
docker-compose exec lpr_service find /app/snapshots/cam_500 -name "*.json" 2>nul | wc -l 2>nul
