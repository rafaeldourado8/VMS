#!/bin/bash

echo "=== Setup VMS Test Environment ==="

# Create superuser
echo "Creating superuser..."
docker exec -it vms_django python manage.py shell <<EOF
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@vms.com', 'admin123')
    print('✓ Superuser created: admin/admin123')
else:
    print('✓ Superuser already exists')
EOF

# Create city
echo "Creating city..."
docker exec -it vms_django python manage.py shell <<EOF
from shared.admin.cidades.models import City
from shared.admin.cidades.enums import CityStatus, Plan
city, created = City.objects.get_or_create(
    name='São Paulo',
    defaults={'status': CityStatus.ACTIVE, 'plan': Plan.PREMIUM}
)
print(f'✓ City: {city.name} (ID: {city.id})')
EOF

# Setup groups
echo "Setting up permission groups..."
docker exec -it vms_django python manage.py setup_groups

echo ""
echo "=== Environment Ready ==="
echo "Admin: http://localhost:8000/admin"
echo "User: admin"
echo "Pass: admin123"
echo ""
echo "Next: Add cameras via admin panel"
