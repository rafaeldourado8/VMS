@echo off
echo ========================================
echo VMS - Quick Setup
echo ========================================
echo.

echo [1/3] Creating superuser...
docker-compose exec -T backend python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@vms.com', 'admin123')
    print('✅ Superuser created: admin/admin123')
else:
    print('✅ Superuser already exists')
EOF

echo.
echo [2/3] Checking services...
curl -s http://localhost:5000/health > nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ AI Detection: OK
) else (
    echo ❌ AI Detection: OFFLINE
)

curl -s http://localhost:8000/admin/login/ > nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Backend: OK
) else (
    echo ❌ Backend: OFFLINE
)

echo.
echo [3/3] System Ready!
echo.
echo ========================================
echo Access Points:
echo ========================================
echo Frontend:  http://localhost:5173
echo Backend:   http://localhost:8000/admin
echo AI API:    http://localhost:5000/cameras
echo HAProxy:   http://localhost:8404
echo.
echo Login: admin / admin123
echo ========================================
