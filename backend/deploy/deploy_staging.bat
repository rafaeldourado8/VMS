@echo off
REM Script de deploy para staging

echo ========================================
echo VMS Backend - Deploy Staging
echo ========================================

echo.
echo [1/6] Parando containers antigos...
docker-compose -f docker-compose.staging.yml down

echo.
echo [2/6] Construindo imagens...
docker-compose -f docker-compose.staging.yml build

echo.
echo [3/6] Iniciando servicos...
docker-compose -f docker-compose.staging.yml up -d

echo.
echo [4/6] Aguardando banco de dados...
timeout /t 10 /nobreak

echo.
echo [5/6] Executando migracoes...
docker-compose -f docker-compose.staging.yml exec backend python manage.py migrate

echo.
echo [6/6] Coletando arquivos estaticos...
docker-compose -f docker-compose.staging.yml exec backend python manage.py collectstatic --noinput

echo.
echo ========================================
echo Deploy concluido!
echo ========================================
echo.
echo Servicos disponiveis:
echo - Backend: http://localhost:8000
echo - Admin: http://localhost:8000/admin
echo.
echo Para ver logs: docker-compose -f docker-compose.staging.yml logs -f
echo Para parar: docker-compose -f docker-compose.staging.yml down
echo.