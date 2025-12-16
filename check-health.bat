@echo off
echo ========================================
echo Verificacao de Saude - GTVision
echo ========================================

echo.
echo [1/5] Status dos Containers:
docker-compose ps

echo.
echo [2/5] Testando Backend (Django):
curl -s http://localhost:8000/admin/login/ | findstr /C:"Django" && echo ✅ Backend OK || echo ❌ Backend FALHOU

echo.
echo [3/5] Testando Kong Gateway:
curl -s http://localhost:8001/ | findstr /C:"version" && echo ✅ Kong OK || echo ❌ Kong FALHOU

echo.
echo [4/5] Testando HAProxy:
curl -s http://localhost:8404/stats | findstr /C:"Statistics" && echo ✅ HAProxy OK || echo ❌ HAProxy FALHOU

echo.
echo [5/5] Testando RabbitMQ:
curl -s http://localhost:15672/ | findstr /C:"RabbitMQ" && echo ✅ RabbitMQ OK || echo ❌ RabbitMQ FALHOU

echo.
echo ========================================
echo Logs Recentes do Celery Worker:
echo ========================================
docker-compose logs --tail=10 backend_worker

echo.
echo ========================================
echo URLs de Acesso:
echo ========================================
echo Frontend:        http://localhost
echo API (Kong):      http://localhost:8000/api/
echo Admin Django:    http://localhost:8000/admin/
echo HAProxy Stats:   http://localhost:8404/stats
echo Kong Admin:      http://localhost:8001/
echo RabbitMQ:        http://localhost:15672/
echo MediaMTX API:    http://localhost:9997/
echo ========================================
