#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.usuarios.models import Usuario

# Deletar usuário existente se houver
Usuario.objects.filter(email='admin@test.com').delete()

# Criar novo superusuário
user = Usuario.objects.create_superuser(
    email='admin@test.com',
    name='Admin',
    password='admin123'
)

print(f'✅ Usuário criado com sucesso!')
print(f'   Email: {user.email}')
print(f'   Nome: {user.name}')
print(f'   Role: {user.role}')
print(f'   Is Staff: {user.is_staff}')
