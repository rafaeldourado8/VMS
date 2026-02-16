@echo off
echo ================================
echo   Limpando e Recriando IAM
echo ================================
echo.

echo [1/4] Removendo tabelas IAM antigas...
docker-compose exec -T postgres_db psql -U gtvision_user -d gtvision_db -c "DROP TABLE IF EXISTS iam_tenantisolation CASCADE;"
docker-compose exec -T postgres_db psql -U gtvision_user -d gtvision_db -c "DROP TABLE IF EXISTS iam_userpermissions CASCADE;"
docker-compose exec -T postgres_db psql -U gtvision_user -d gtvision_db -c "DROP TABLE IF EXISTS iam_iamrule CASCADE;"
docker-compose exec -T postgres_db psql -U gtvision_user -d gtvision_db -c "DROP TABLE IF EXISTS iam_iampermission CASCADE;"
echo.

echo [2/4] Removendo registro de migrations...
docker-compose exec -T postgres_db psql -U gtvision_user -d gtvision_db -c "DELETE FROM django_migrations WHERE app='iam';"
echo.

echo [3/4] Aplicando migrations IAM...
docker-compose exec backend python manage.py migrate iam
echo.

echo [4/4] Carregando permissoes...
docker-compose exec backend python manage.py load_permissions
echo.

echo ================================
echo   IAM configurado com sucesso!
echo ================================
echo.
pause
