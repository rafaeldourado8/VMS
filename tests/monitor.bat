@echo off
:loop
cls
echo ========================================
echo MONITORAMENTO LPR - Camera 777
echo ========================================
echo.
echo Ultimas deteccoes:
docker-compose exec lpr_service find /app/snapshots/cam_777 -name "metadata.json" 2>nul | wc -l 2>nul
echo.
echo Ultimo snapshot:
docker-compose exec lpr_service find /app/snapshots/cam_777 -name "metadata.json" -exec tail -1 {} \; 2>nul | tail -1
echo.
timeout /t 5 /nobreak >nul
goto loop
