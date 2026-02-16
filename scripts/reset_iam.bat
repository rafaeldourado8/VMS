@echo off
echo ================================
echo   Reset Completo IAM
echo ================================
echo.

echo [1/6] Parando backend...
docker-compose stop backend
echo.

echo [2/6] Removendo tabelas IAM...
docker-compose exec -T postgres_db psql -U gtvision_user -d gtvision_db -c "DROP TABLE IF EXISTS iam_tenantisolation CASCADE;"
docker-compose exec -T postgres_db psql -U gtvision_user -d gtvision_db -c "DROP TABLE IF EXISTS iam_userpermissions CASCADE;"
docker-compose exec -T postgres_db psql -U gtvision_user -d gtvision_db -c "DROP TABLE IF EXISTS iam_iamrule CASCADE;"
docker-compose exec -T postgres_db psql -U gtvision_user -d gtvision_db -c "DROP TABLE IF EXISTS iam_iampermission CASCADE;"
docker-compose exec -T postgres_db psql -U gtvision_user -d gtvision_db -c "DELETE FROM django_migrations WHERE app='iam';"
echo.

echo [3/6] Rebuilding backend...
docker-compose build backend
echo.

echo [4/6] Iniciando backend...
docker-compose up -d backend
echo.

echo [5/6] Aguardando backend (30s)...
timeout /t 30 /nobreak
echo.

echo [6/6] Aplicando migrations e carregando permissoes...
docker-compose exec backend python manage.py migrate iam
docker-compose exec backend python manage.py load_permissions
echo.

echo ================================
echo   IAM configurado!
echo ================================
echo.
pause
