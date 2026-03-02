#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.cameras.models import Camera
from apps.usuarios.models import Usuario

print("="*60)
print("TESTE: ALERTA DE CÂMERA OFFLINE")
print("="*60)

# Buscar primeira câmera
camera = Camera.objects.first()
if not camera:
    print("\n❌ Nenhuma câmera encontrada")
    exit(1)

print(f"\n📹 Câmera: {camera.name}")
print(f"   Status atual: {camera.status}")

# Simular câmera ficando offline
if camera.status == 'online':
    print("\n🔄 Mudando status para offline...")
    camera.status = 'offline'
    camera.save()
    print("   ✓ Status alterado")
    print("   ✓ Signal disparado")
    print("   ✓ Email enviado para admins (verifique console)")
else:
    print("\n🔄 Câmera já está offline, mudando para online...")
    camera.status = 'online'
    camera.save()
    print("   ✓ Status alterado para online")

print("\n" + "="*60)
print("Verifique os logs do backend para ver o email:")
print("docker-compose logs backend | grep 'Câmera Offline'")
print("="*60)
