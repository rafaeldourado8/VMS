#!/usr/bin/env python
"""Script para adicionar câmera de teste"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.cameras.models import Camera

# Criar câmera de teste
camera, created = Camera.objects.get_or_create(
    nome="Câmera Teste 1",
    defaults={
        "rtsp_url": "rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mp4",
        "localizacao": "Teste",
        "ativo": True,
        "descricao": "Câmera de teste com stream público"
    }
)

if created:
    print(f"✅ Câmera criada: {camera.nome} (ID: {camera.id})")
    print(f"   RTSP: {camera.rtsp_url}")
    print(f"   HLS: http://localhost:8888/{camera.id}/index.m3u8")
else:
    print(f"ℹ️  Câmera já existe: {camera.nome} (ID: {camera.id})")

print("\n📝 Para testar o stream:")
print(f"   1. Publique o RTSP no MediaMTX:")
print(f"      ffmpeg -re -i {camera.rtsp_url} -c copy -f rtsp rtsp://localhost:8554/{camera.id}")
print(f"   2. Acesse o HLS em: http://localhost:8888/{camera.id}/index.m3u8")
