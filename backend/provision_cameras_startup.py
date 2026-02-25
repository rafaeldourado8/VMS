#!/usr/bin/env python3
"""Provisiona todas as câmeras ativas no startup do backend"""
import os
import sys
import django
import httpx
import time

sys.path.insert(0, '/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.cameras.models import Camera

STREAMING_API = os.getenv('STREAMING_API_URL', 'http://streaming:8001')
MAX_RETRIES = 10
RETRY_DELAY = 3

def wait_for_streaming():
    """Aguarda streaming service ficar disponível."""
    print("⏳ Aguardando streaming service...")
    for i in range(MAX_RETRIES):
        try:
            resp = httpx.get(f"{STREAMING_API}/health", timeout=5.0)
            if resp.status_code == 200:
                print("✅ Streaming service disponível")
                return True
        except:
            pass
        print(f"   Tentativa {i+1}/{MAX_RETRIES}...")
        time.sleep(RETRY_DELAY)
    return False

def provision_all_cameras():
    """Provisiona todas as câmeras ativas."""
    cameras = Camera.objects.filter(status='online')
    total = cameras.count()
    
    if total == 0:
        print("ℹ️  Nenhuma câmera ativa para provisionar")
        return
    
    print(f"🔄 Provisionando {total} câmeras...")
    
    success = 0
    failed = 0
    
    with httpx.Client(timeout=30.0) as client:
        for camera in cameras:
            try:
                resp = client.post(
                    f"{STREAMING_API}/cameras/provision",
                    json={
                        "camera_id": camera.id,
                        "rtsp_url": camera.stream_url,
                        "name": camera.name,
                        "enabled": True,
                        "on_demand": True
                    }
                )
                if resp.status_code == 200:
                    print(f"✅ cam_{camera.id} - {camera.name}")
                    success += 1
                else:
                    print(f"❌ cam_{camera.id} - {resp.text}")
                    failed += 1
            except Exception as e:
                print(f"❌ cam_{camera.id} - {e}")
                failed += 1
            
            time.sleep(1)
    
    print(f"\n📊 Resultado: {success} sucesso, {failed} falhas de {total} total")

if __name__ == "__main__":
    print("=" * 50)
    print("🚀 Startup: Provisionamento de Câmeras")
    print("=" * 50)
    
    if wait_for_streaming():
        provision_all_cameras()
        print("\n✅ Provisionamento concluído!")
    else:
        print("\n⚠️  Streaming service não disponível, continuando...")
