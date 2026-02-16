@echo off
echo ================================
echo   Fix Final - Backend
echo ================================
echo.

echo [1/4] Parando backend...
docker-compose stop backend
echo.

echo [2/4] Limpando IAM do banco...
docker-compose exec -T postgres_db psql -U gtvision_user -d gtvision_db -c "DROP TABLE IF EXISTS iam_tenantisolation CASCADE;"
docker-compose exec -T postgres_db psql -U gtvision_user -d gtvision_db -c "DROP TABLE IF EXISTS iam_userpermissions CASCADE;"
docker-compose exec -T postgres_db psql -U gtvision_user -d gtvision_db -c "DROP TABLE IF EXISTS iam_iamrule CASCADE;"
docker-compose exec -T postgres_db psql -U gtvision_user -d gtvision_db -c "DROP TABLE IF EXISTS iam_iampermission CASCADE;"
docker-compose exec -T postgres_db psql -U gtvision_user -d gtvision_db -c "DELETE FROM django_migrations WHERE app='iam';"
echo.

echo [3/4] Rebuilding e iniciando backend...
docker-compose build backend
docker-compose up -d backend
timeout /t 40 /nobreak
echo.

echo [4/4] Aplicando migrations IAM...
docker-compose exec backend python manage.py migrate iam
docker-compose exec backend python manage.py load_permissions
echo.

echo ================================
echo   Sistema Corrigido!
echo ================================
echo.
echo Acesse:
echo   - Visao Tatica: http://localhost/cameras/tactical
echo   - Retencao: http://localhost/settings/retention  
echo   - IAM: http://localhost/settings/iam
echo.
pause
