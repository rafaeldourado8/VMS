#!/bin/bash
# Criar usuário de teste

docker-compose exec -T backend python manage.py shell <<EOF
from apps.usuarios.models import Usuario
if not Usuario.objects.filter(email='admin@test.com').exists():
    Usuario.objects.create_superuser(
        email='admin@test.com',
        name='Admin Test',
        password='admin123'
    )
    print('✅ Usuário criado: admin@test.com / admin123')
else:
    print('⚠️ Usuário já existe')
EOF
