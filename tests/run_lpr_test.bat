@echo off
echo ========================================
echo TESTE DO SISTEMA LPR
echo ========================================
echo.

echo [1/4] Verificando servicos...
docker-compose ps lpr_service mediamtx redis_cache
echo.

echo [2/4] Iniciando stream de teste no MediaMTX...
start /B docker-compose exec -d mediamtx sh -c "ffmpeg -re -stream_loop -1 -i /app/test_video.mp4 -c copy -f rtsp rtsp://localhost:8554/test_video"
timeout /t 5 /nobreak >nul
echo.

echo [3/4] Publicando cameras no Redis...
docker-compose exec -T lpr_service python -c "import redis,json,time;r=redis.Redis(host='redis_cache',port=6379,db=2);r.ping();[r.publish('camera:provisioned',json.dumps(c)) or time.sleep(1) for c in [{'camera_id':999,'rtsp_url':'rtsp://mediamtx:8554/test_video'},{'camera_id':555,'rtsp_url':'/app/test_video.mp4'}]];print('OK')"
echo.

echo [4/4] Aguardando processamento (30s)...
timeout /t 30 /nobreak
echo.

echo ========================================
echo VERIFICANDO RESULTADOS
echo ========================================
echo.

echo Logs do LPR (ultimas 50 linhas):
docker-compose logs --tail=50 lpr_service
echo.

echo Snapshots gerados:
docker-compose exec lpr_service sh -c "find /app/snapshots -type d -name 'cam_*' -exec echo '{}:' \; -exec find '{}' -maxdepth 1 -type d | wc -l \;"
echo.

echo Estrutura de snapshots:
docker-compose exec lpr_service sh -c "ls -lR /app/snapshots | head -50"
echo.

echo ========================================
echo TESTE CONCLUIDO
echo ========================================
echo.
echo Para ver logs em tempo real:
echo   docker-compose logs -f lpr_service
echo.
echo Para verificar snapshots:
echo   docker-compose exec lpr_service ls -lR /app/snapshots
echo.
