@echo off
REM Rebuild Streaming Services com Fallback
echo ========================================
echo Rebuild: Streaming + Health Check + Monitor
echo ========================================
echo.

echo [1/4] Parando servicos...
docker-compose stop streaming mediamtx_monitor stream_health
echo.

echo [2/4] Removendo containers...
docker-compose rm -f streaming mediamtx_monitor stream_health
echo.

echo [3/4] Rebuild da imagem...
docker-compose build streaming
echo.

echo [4/4] Iniciando servicos...
docker-compose up -d streaming mediamtx_monitor stream_health
echo.

echo ========================================
echo Aguardando servicos ficarem prontos...
echo ========================================
timeout /t 10 /nobreak

echo.
echo Verificando status:
docker-compose ps streaming mediamtx_monitor stream_health
echo.

echo Logs do streaming:
docker logs --tail 20 gtvision_streaming
echo.

echo ========================================
echo Rebuild concluido!
echo.
echo Servicos disponiveis:
echo - Streaming API: http://localhost:8001
echo - Health Check: docker logs -f gtvision_stream_health
echo - MediaMTX Monitor: docker logs -f gtvision_mediamtx_monitor
echo ========================================
