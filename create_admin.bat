@echo off
echo Creating superuser...
echo.
docker-compose exec backend python -c "import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings'); import django; django.setup(); from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(email='admin@vms.com').exists() or User.objects.create_superuser(email='admin@vms.com', password='admin123', name='Admin User'); print('✅ Superuser: admin@vms.com / admin123')"
echo.
echo Done!
pause
