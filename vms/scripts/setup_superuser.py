from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@vms.com', 'admin123')
    print('✓ Superuser created: admin/admin123')
else:
    print('✓ Superuser already exists')
