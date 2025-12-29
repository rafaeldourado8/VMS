@echo off
echo 🎥 INICIANDO VMS - CONFIGURAÇÃO 12 CÂMERAS
echo ==========================================

echo 🔧 Configurações aplicadas:
echo   • MediaMTX: 2.5 CPU, 2GB RAM
echo   • HLS: 2 segmentos de 2s (ultra baixa latência)
echo   • Streaming: 2 workers otimizados
echo   • Nginx: Cache agressivo para HLS
echo   • Player: Buffer mínimo (3s)

echo.
echo ⏹️ Parando sistema anterior...
docker-compose down
docker-compose -f docker-compose.minimal.yml down

echo.
echo 🚀 Iniciando sistema para 12 câmeras...
docker-compose -f docker-compose.12cam.yml up -d

echo.
echo ⏳ Aguardando serviços ficarem prontos...
timeout /t 15 /nobreak > nul

echo.
echo 📊 Status dos serviços:
docker-compose -f docker-compose.12cam.yml ps

echo.
echo ✅ Sistema iniciado!
echo.
echo 🔗 ENDPOINTS:
echo   • API Health: http://localhost:8001/health
echo   • API Stats:  http://localhost:8001/stats
echo   • Frontend:   http://localhost:80
echo.
echo 📝 PROVISIONAR CÂMERA:
echo curl -X POST http://localhost:8001/cameras/provision \
echo   -H "Content-Type: application/json" \
echo   -d "{\"camera_id\": 1, \"rtsp_url\": \"rtsp://sua-camera\", \"name\": \"Cam1\"}"
echo.
echo 🎬 STREAM HLS:
echo http://localhost/hls/cam_1/index.m3u8
echo.
echo 📈 MONITORAR:
echo docker stats

pause