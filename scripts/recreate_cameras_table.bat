@echo off
cd /d d:\VMS
echo Removendo migracoes antigas...
docker-compose exec backend rm -f /app/apps/cameras/migrations/0001_initial.py
docker-compose exec backend rm -f /app/apps/cameras/migrations/__pycache__/0001_initial.cpython-*.pyc

echo Criando nova migracao...
docker-compose exec backend python manage.py makemigrations cameras

echo Aplicando migracao...
docker-compose exec backend python manage.py migrate cameras

echo Pronto!
pause
