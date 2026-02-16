@echo off
cd /d d:\VMS\backend
docker-compose exec backend python manage.py migrate cameras
pause
