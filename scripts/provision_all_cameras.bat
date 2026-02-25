@echo off
echo ========================================
echo Provisionando todas as cameras
echo ========================================
echo.

echo Buscando cameras do banco...
for /f "tokens=*" %%i in ('docker exec gtvision_backend python -c "import os, sys, django; sys.path.insert(0, '/app'); os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings'); django.setup(); from apps.cameras.models import Camera; cameras = Camera.objects.filter(status='online'); import json; print(json.dumps([{'id': c.id, 'name': c.name, 'stream_url': c.stream_url} for c in cameras]))"') do set CAMERAS=%%i

echo Cameras encontradas: %CAMERAS%
echo.

echo Provisionando via streaming service...
docker exec gtvision_backend python -c "import os, sys, django, httpx, json; sys.path.insert(0, '/app'); os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings'); django.setup(); from apps.cameras.models import Camera; cameras = Camera.objects.filter(status='online'); client = httpx.Client(timeout=30.0); [print(f'cam_{c.id}: {client.post(\"http://streaming:8001/cameras/provision\", json={\"camera_id\": c.id, \"rtsp_url\": c.stream_url, \"name\": c.name, \"enabled\": True, \"on_demand\": True}).json()}') for c in cameras]"

echo.
echo ========================================
echo Concluido!
echo ========================================
