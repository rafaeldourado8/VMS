@echo off
echo ================================
echo   Setup IAM no Docker
echo ================================
echo.

echo [1/3] Aplicando migrations IAM...
docker-compose exec backend python manage.py makemigrations iam
docker-compose exec backend python manage.py migrate iam
echo.

echo [2/3] Carregando permissoes iniciais...
docker-compose exec backend python manage.py load_permissions
echo.

echo [3/3] Criando usuario admin...
docker-compose exec backend python manage.py shell -c "from apps.usuarios.models import Usuario; Usuario.objects.filter(email='admin@vms.com').exists() or Usuario.objects.create_superuser(email='admin@vms.com', name='Administrator', password='admin123') and print('Usuario admin criado: admin@vms.com / admin123')"
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
