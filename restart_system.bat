@echo off
echo 🔄 REINICIANDO DOCKER E SISTEMA VMS
echo ==========================================

echo ⏹️ Parando Docker Desktop...
taskkill /F /IM "Docker Desktop.exe" 2>nul
timeout /t 5 /nobreak > nul

echo 🚀 Iniciando Docker Desktop...
start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
timeout /t 30 /nobreak > nul

echo 🧹 Limpando containers antigos...
docker system prune -f

echo 📦 Iniciando apenas serviços essenciais (sem IA)...
docker-compose up -d mediamtx streaming redis_cache postgres_db backend frontend kong haproxy

echo ✅ Sistema iniciado!
echo.
echo 📝 Para adicionar IA depois:
echo docker-compose up -d rabbitmq_ai redis_ai postgres_ai
echo docker-compose up -d ai_worker_1 ai_worker_2

pause