@echo off
echo ================================
echo   Configurando IAM
echo ================================
echo.

echo [1/4] Aplicando migrations...
python manage.py makemigrations iam
python manage.py migrate iam
echo.

echo [2/4] Carregando permissoes iniciais...
python manage.py load_permissions
echo.

echo [3/4] Verificando usuario admin...
python manage.py shell -c "from apps.usuarios.models import Usuario; Usuario.objects.filter(email='admin@vms.com').exists() or Usuario.objects.create_superuser(email='admin@vms.com', name='Administrator', password='admin123') and print('Usuario admin criado: admin@vms.com / admin123')"
echo.

echo [4/4] Concluido!
echo.
echo ================================
echo   IAM configurado com sucesso!
echo ================================
echo.
echo Proximos passos:
echo   1. Acesse /admin para gerenciar permissoes
echo   2. Acesse /settings/iam no frontend
echo   3. Crie usuarios e atribua permissoes
echo.
pause
