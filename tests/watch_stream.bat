@echo off
cls
echo ========================================
echo   SISTEMA LPR COM VISUALIZACAO
echo ========================================
echo.
echo Stream RTSP: rtsp://localhost:8554/cam_400_ai
echo.
echo Abra no VLC:
echo   vlc rtsp://localhost:8554/cam_400_ai
echo.
echo ========================================
echo.
echo Aguardando deteccoes (pressione Ctrl+C para sair)...
echo.

:loop
timeout /t 5 /nobreak >nul
docker-compose logs --tail=5 lpr_service 2>nul | findstr /C:"SAVED" /C:"Tracked" 2>nul
goto loop
