@echo off
echo ========================================
echo Aplicando Migration - Clips Protection
echo ========================================
echo.

echo [1/2] Criando migration...
docker-compose exec backend python manage.py makemigrations clips

echo.
echo [2/2] Aplicando migration...
docker-compose exec backend python manage.py migrate clips

echo.
echo ========================================
echo Migration aplicada!
echo ========================================
echo.
echo Agora os clips:
echo - Nao serao deletados se camera for excluida
echo - Nao serao afetados pela retencao automatica
echo - Tem backup de camera_id e camera_name
echo.
pause
