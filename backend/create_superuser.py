import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

if not User.objects.filter(email='admin@vms.com').exists():
    User.objects.create_superuser(
        email='admin@vms.com',
        password='admin123',
        name='Admin User'
    )
    print('✅ Superuser created: admin@vms.com / admin123')
else:
    print('✅ Superuser already exists: admin@vms.com / admin123')
