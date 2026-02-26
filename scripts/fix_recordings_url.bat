@echo off
echo Reiniciando Backend...
docker-compose restart backend
timeout /t 5 /nobreak >nul
echo.
echo Testando endpoint...
curl -I "http://localhost/api/recordings/serve/2/2026-02-26/08-52-10/"
echo.
pause
