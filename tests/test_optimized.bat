@echo off
echo Aguardando servico iniciar...
timeout /t 15 /nobreak >nul

echo Instalando EasyOCR...
docker-compose exec lpr_service pip install easyocr

echo Aguardando 10s...
timeout /t 10 /nobreak >nul

echo Limpando snapshots antigos...
docker-compose exec lpr_service rm -rf /app/snapshots/*

echo Reiniciando servico...
docker-compose restart lpr_service

echo Aguardando 20s...
timeout /t 20 /nobreak >nul

echo Publicando camera 100...
docker-compose exec lpr_service python -c "import redis,json;r=redis.Redis(host='redis_cache',port=6379,db=2);r.publish('camera:provisioned',json.dumps({'camera_id':100,'rtsp_url':'/app/test_video.mp4'}))"

echo Processando por 60s...
timeout /t 60 /nobreak >nul

echo.
echo === RESULTADOS ===
docker-compose exec lpr_service find /app/snapshots -name "metadata.json" -exec cat {} \;

echo.
echo === LOGS ===
docker-compose logs --tail=30 lpr_service | findstr /C:"[SAVED]" /C:"Placa:"
