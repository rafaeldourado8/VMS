@echo off
echo 🔧 Aplicando correções de drift no VMS...

REM Para os serviços
echo ⏹️ Parando serviços...
docker-compose down

REM Remove containers antigos para forçar rebuild
echo 🗑️ Removendo containers antigos...
docker-compose rm -f mediamtx streaming

REM Rebuild apenas os serviços necessários
echo 🔨 Rebuilding serviços com correções...
docker-compose build --no-cache streaming

REM Inicia os serviços
echo 🚀 Iniciando serviços corrigidos...
docker-compose up -d

REM Aguarda os serviços ficarem prontos
echo ⏳ Aguardando serviços ficarem prontos...
timeout /t 10 /nobreak > nul

REM Verifica status
echo 📊 Status dos serviços:
docker-compose ps

echo.
echo ✅ Correções aplicadas!
echo.
echo 🔍 Principais correções implementadas:
echo   • useAbsoluteTimestamp: false (evita drift)
echo   • Buffer HLS otimizado (3 segmentos de 4s)
echo   • Timeouts aumentados para estabilidade
echo   • Monitor automático de drift
echo   • Player frontend otimizado
echo.
echo 📝 Monitoramento:
echo   • Logs MediaMTX: docker-compose logs -f mediamtx
echo   • Logs Streaming: docker-compose logs -f streaming
echo   • Stats: curl http://localhost:8001/stats

pause