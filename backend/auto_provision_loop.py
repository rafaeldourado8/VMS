#!/usr/bin/env python3
"""Auto-provision loop - roda continuamente"""
import time
import httpx
import os
import sys
import django

sys.path.insert(0, '/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.cameras.models import Camera

STREAMING_URL = 'http://streaming:8001'
CHECK_INTERVAL = 60

print("🔄 Auto-provision loop iniciado")

while True:
    try:
        # Verifica se streaming está up
        try:
            httpx.get(f"{STREAMING_URL}/health", timeout=3)
        except:
            time.sleep(10)
            continue
        
        # Busca câmeras ativas
        cameras = Camera.objects.filter(status='online')
        
        # Provisiona cada uma
        with httpx.Client(timeout=30.0) as client:
            for camera in cameras:
                try:
                    resp = client.get(f"{STREAMING_URL}/cameras/{camera.id}/status", timeout=5)
                    if resp.status_code != 200 or resp.json().get('status') == 'not_found':
                        # Câmera não provisionada, provisionar
                        client.post(
                            f"{STREAMING_URL}/cameras/provision",
                            json={
                                'camera_id': camera.id,
                                'rtsp_url': camera.stream_url,
                                'name': camera.name,
                                'enabled': True,
                                'on_demand': True
                            }
                        )
                        print(f"✅ cam_{camera.id} provisionada")
                except:
                    pass
        
    except Exception as e:
        print(f"⚠️ Erro: {e}")
    
    time.sleep(CHECK_INTERVAL)
