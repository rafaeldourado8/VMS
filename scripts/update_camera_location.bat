@echo off
echo ========================================
echo Atualizando modelo Camera - Location obrigatorio
echo ========================================

cd /d d:\VMS\backend

echo.
echo [1/3] Criando migracao...
docker-compose exec backend python manage.py makemigrations cameras --name make_location_required

echo.
echo [2/3] Aplicando migracao...
docker-compose exec backend python manage.py migrate cameras

echo.
echo [3/3] Verificando...
docker-compose exec backend python manage.py showmigrations cameras

echo.
echo ========================================
echo Concluido!
echo ========================================
pause
