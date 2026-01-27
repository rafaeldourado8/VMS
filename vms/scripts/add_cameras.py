from shared.admin.cidades.models import City
from shared.admin.cameras.models import Camera
from shared.admin.cameras.enums import CameraProtocol

city = City.objects.first()
if not city:
    print("❌ Nenhuma cidade encontrada!")
    exit(1)

print(f"✓ Cidade: {city.name} (ID: {city.id})")
print("\n=== Adicionando Câmeras ===\n")

# RTSP Cameras
rtsp_cameras = [
    ("Câmera RTSP 01", "rtsp://admin:Camerite123@45.236.226.75:6053/cam/realmonitor?channel=1&subtype=0"),
    ("Câmera RTSP 02", "rtsp://admin:Camerite123@45.236.226.75:6052/cam/realmonitor?channel=1&subtype=0"),
    ("Câmera RTSP 03", "rtsp://admin:Camerite123@45.236.226.72:6049/cam/realmonitor?channel=1&subtype=0"),
    ("Câmera RTSP 04", "rtsp://admin:Camerite123@45.236.226.71:6047/cam/realmonitor?channel=1&subtype=0"),
    ("Câmera RTSP 05", "rtsp://admin:Camerite123@45.236.226.71:6046/cam/realmonitor?channel=1&subtype=0"),
    ("Câmera RTSP 06", "rtsp://admin:Camerite123@45.236.226.70:6045/cam/realmonitor?channel=1&subtype=0"),
    ("Câmera RTSP 07", "rtsp://admin:Camerite123@45.236.226.70:6044/cam/realmonitor?channel=1&subtype=0"),
]

# RTMP Cameras
rtmp_cameras = [
    ("Câmera RTMP 01", "rtmp://inst-iwvio-srs-rtmp-intelbras.camerite.services:1935/record/7KOM27157189T.stream"),
    ("Câmera RTMP 02", "rtmp://inst-qbpq0-srs-rtmp-intelbras.camerite.services:1935/record/7KOM2701234EA.stream"),
    ("Câmera RTMP 03", "rtmp://inst-iwvio-srs-rtmp-intelbras.camerite.services:1935/record/7KOM2715569J7.stream"),
    ("Câmera RTMP 04", "rtmp://inst-t4ntf-srs-rtmp-intelbras.camerite.services:1935/record/7KOM2715576GO.stream"),
]

# Add RTSP cameras
for name, url in rtsp_cameras:
    camera, created = Camera.objects.get_or_create(
        city=city,
        name=name,
        defaults={
            'stream_url': url,
            'protocol': CameraProtocol.RTSP,
            'is_active': True,
            'is_lpr': False
        }
    )
    status = "✓ Criada" if created else "✓ Já existe"
    print(f"{status}: {name} | Public ID: {camera.public_id}")

# Add RTMP cameras
for name, url in rtmp_cameras:
    camera, created = Camera.objects.get_or_create(
        city=city,
        name=name,
        defaults={
            'stream_url': url,
            'protocol': CameraProtocol.RTMP,
            'is_active': True,
            'is_lpr': False
        }
    )
    status = "✓ Criada" if created else "✓ Já existe"
    print(f"{status}: {name} | Public ID: {camera.public_id}")

print(f"\n✓ Total: {Camera.objects.filter(city=city).count()} câmeras")
