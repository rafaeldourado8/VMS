@echo off
timeout /t 20 /nobreak
docker-compose exec lpr_service ls /app/snapshots/cam_777 2>nul
