@echo off
echo 🔍 MONITORAMENTO VMS - SISTEMA OTIMIZADO
echo ==========================================

:loop
cls
echo 📊 RECURSOS ATUAIS:
docker stats --no-stream

echo.
echo 🎯 SERVIÇOS ATIVOS:
docker-compose -f docker-compose.minimal.yml ps

echo.
echo 🔗 ENDPOINTS DISPONÍVEIS:
echo   • Health Check: http://localhost:8001/health
echo   • Stats API:    http://localhost:8001/stats
echo   • Streams:      http://localhost:8001/streams
echo   • Frontend:     http://localhost:80

echo.
echo 📝 COMANDOS ÚTEIS:
echo   • Provisionar câmera: curl -X POST http://localhost:8001/cameras/provision -H "Content-Type: application/json" -d "{\"camera_id\": 1, \"rtsp_url\": \"rtsp://sua-camera\", \"name\": \"Cam1\"}"
echo   • Ver logs MediaMTX:  docker-compose -f docker-compose.minimal.yml logs -f mediamtx
echo   • Ver logs Streaming: docker-compose -f docker-compose.minimal.yml logs -f streaming

echo.
echo ⏰ Próxima atualização em 10 segundos... (Ctrl+C para sair)
timeout /t 10 /nobreak > nul
goto loop