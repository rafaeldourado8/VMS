@echo off
echo === TESTE SISTEMA OTIMIZADO ===
echo.
echo Aguardando 15s...
timeout /t 15 /nobreak >nul

echo Limpando snapshots...
docker-compose exec lpr_service rm -rf /app/snapshots/*

echo Publicando camera 200...
docker-compose exec lpr_service python -c "import redis,json;r=redis.Redis(host='redis_cache',port=6379,db=2);r.publish('camera:provisioned',json.dumps({'camera_id':200,'rtsp_url':'/app/test_video.mp4'}))"

echo Processando 45s...
timeout /t 45 /nobreak >nul

echo.
echo === RESULTADOS ===
docker-compose exec lpr_service find /app/snapshots -name "*.json" | wc -l 2>nul
docker-compose exec lpr_service find /app/snapshots -name "metadata.json" -print -exec cat {} \; 2>nul

echo.
echo === LOGS ===
docker-compose logs --tail=20 lpr_service | findstr /C:"[SAVED]"
