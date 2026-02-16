@echo off
echo ================================
echo   Rebuild Backend + Setup IAM
echo ================================
echo.

echo [1/5] Parando backend...
docker-compose stop backend
echo.

echo [2/5] Rebuilding backend com IAM...
docker-compose build backend
echo.

echo [3/5] Iniciando backend...
docker-compose up -d backend
echo.

echo [4/5] Aguardando backend iniciar (30s)...
timeout /t 30 /nobreak
echo.

echo [5/5] Aplicando migrations e configurando IAM...
docker-compose exec backend python manage.py makemigrations iam
docker-compose exec backend python manage.py migrate iam
docker-compose exec backend python manage.py load_permissions
echo.

echo ================================
echo   IAM configurado com sucesso!
echo ================================
echo.
echo Acesse:
echo   Frontend: http://localhost/settings/iam
echo   Admin: http://localhost/admin
echo.
echo Login:
echo   Email: admin@vms.com
echo   Senha: admin123
echo.
pause
