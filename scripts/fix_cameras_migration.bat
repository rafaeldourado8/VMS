@echo off
cd /d d:\VMS
echo Copiando migracao para container...
docker cp backend\apps\cameras\migrations\0001_initial.py gtvision_backend:/app/apps/cameras/migrations/0001_initial.py
echo Aplicando migracao...
docker-compose exec backend python manage.py migrate cameras --fake
echo Pronto!
pause
