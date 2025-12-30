@echo off
echo ========================================
echo VERIFICAÇÃO FINAL DO VMS
echo ========================================

echo Verificando status dos serviços...
docker-compose ps

echo.
echo ========================================
echo TESTANDO ENDPOINTS
echo ========================================

echo Testando Frontend...
curl -s -o nul -w "Frontend: %%{http_code}\n" http://localhost || echo Frontend: ERRO

echo Testando HAProxy Stats...
curl -s -o nul -w "HAProxy Stats: %%{http_code}\n" http://localhost:8404 || echo HAProxy Stats: ERRO

echo Testando MediaMTX API...
curl -s -o nul -w "MediaMTX API: %%{http_code}\n" http://localhost:9997/v3/config/global/get || echo MediaMTX API: ERRO

echo Testando Streaming Service...
curl -s -o nul -w "Streaming Service: %%{http_code}\n" http://localhost:8001/health || echo Streaming Service: ERRO

echo.
echo ========================================
echo LOGS RECENTES (últimas 3 linhas)
echo ========================================

echo --- Frontend ---
docker-compose logs --tail=3 frontend

echo --- Backend ---
docker-compose logs --tail=3 backend

echo --- MediaMTX ---
docker-compose logs --tail=3 mediamtx

echo --- AI Workers ---
docker-compose logs --tail=2 ai_worker_1
docker-compose logs --tail=2 ai_worker_2

echo.
echo ========================================
echo SISTEMA PRONTO!
echo ========================================
echo Frontend: http://localhost
echo HAProxy Stats: http://localhost:8404
echo MediaMTX API: http://localhost:9997
echo Streaming Service: http://localhost:8001
echo ========================================