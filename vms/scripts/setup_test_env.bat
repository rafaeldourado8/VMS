@echo off
echo === Setup VMS Test Environment ===
echo.

echo Creating superuser...
docker exec -i vms_django python manage.py shell < setup_superuser.py

echo.
echo Creating city...
docker exec -i vms_django python manage.py shell < setup_city.py

echo.
echo Setting up permission groups...
docker exec -it vms_django python manage.py setup_groups

echo.
echo === Environment Ready ===
echo Admin: http://localhost:8000/admin
echo User: admin
echo Pass: admin123
echo.
echo Next: Add cameras via admin panel
pause
