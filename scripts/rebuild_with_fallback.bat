@echo off
echo ========================================
echo REBUILD COMPLETO - Sistema de Fallback
echo ========================================
echo.

echo [1/6] Parando servicos...
docker-compose stop backend streaming stream_health mediamtx_monitor
echo.

echo [2/6] Removendo containers...
docker-compose rm -f backend streaming stream_health mediamtx_monitor
echo.

echo [3/6] Rebuild das imagens...
docker-compose build backend streaming
echo.

echo [4/6] Iniciando servicos...
docker-compose up -d postgres_db redis_cache mediamtx
timeout /t 15 /nobreak
docker-compose up -d streaming
timeout /t 10 /nobreak
docker-compose up -d backend stream_health mediamtx_monitor
echo.

echo [5/6] Aguardando servicos ficarem prontos (60s)...
timeout /t 60 /nobreak
echo.

echo [6/6] Verificando status...
docker-compose ps backend streaming stream_health
echo.

echo ========================================
echo Verificando cameras provisionadas...
echo ========================================
curl -s http://localhost:8001/stats
echo.
echo.

echo ========================================
echo Logs do backend (startup):
echo ========================================
docker logs gtvision_backend --tail 30
echo.

echo ========================================
echo REBUILD CONCLUIDO!
echo ========================================
echo.
echo Teste no navegador: http://localhost
echo.
