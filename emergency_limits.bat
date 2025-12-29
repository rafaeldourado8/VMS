@echo off
echo 🚨 APLICANDO LIMITAÇÕES EXTREMAS DE CPU...

REM Para todos os serviços
docker-compose down

REM Remove containers para forçar rebuild
docker-compose rm -f

echo 🔧 Configurações aplicadas:
echo   • MediaMTX: 1 CPU, 1GB RAM
echo   • Streaming: 1 worker
echo   • Backend: 1 worker  
echo   • HLS: 2 segmentos, sem remux
echo   • SEM GRAVAÇÃO (economia máxima)
echo   • Máximo 2 viewers por câmera

REM Inicia apenas serviços essenciais
echo 🚀 Iniciando com limitações...
docker-compose up -d postgres_db redis_cache
timeout /t 10 /nobreak > nul

docker-compose up -d mediamtx
timeout /t 5 /nobreak > nul

docker-compose up -d streaming backend
timeout /t 5 /nobreak > nul

docker-compose up -d frontend nginx haproxy

echo ✅ Sistema iniciado com limitações extremas
echo ⚠️  GRAVAÇÃO DESABILITADA para economizar CPU
echo 📊 Monitore: docker stats

pause