from apps.cameras.models import Camera
from django.contrib.auth import get_user_model
from django.db import IntegrityError

User = get_user_model()
admin = User.objects.first()

cameras = [
    {"name": "LPR AV. AREADO - CAMERA 1", "stream_url": "rtsp://admin:Camerite123@45.236.226.72:6048/cam/realmonitor?channel=1&subtype=0", "location": "Av. Areado"},
    {"name": "LPR BR 060 - CAMERA 1", "stream_url": "rtsp://admin:Camerite123@45.236.226.71:6047/cam/realmonitor?channel=1&subtype=0", "location": "BR 060"},
    {"name": "LPR MS 338 - Saida Para Ribas - CARGIL - CAM 2", "stream_url": "rtsp://admin:Camerite123@45.236.226.70:6045/cam/realmonitor?channel=1&subtype=0", "location": "MS 338 - Cargil"},
    {"name": "LPR MS 338 - Saida Para Ribas - CARGIL - CAM 1", "stream_url": "rtsp://admin:Camerite123@45.236.226.70:6044/cam/realmonitor?channel=1&subtype=0", "location": "MS 338 - Cargil"},
    {"name": "LPR Av Weimar G. Torres - CAM 2", "stream_url": "rtsp://admin:Camerite@186.226.193.111:602/h264/ch1/main/av_stream", "location": "Av. Weimar G. Torres - Navirai"},
    {"name": "LPR Av. Amelia Fukuda - EXPONAVI - CAM 1", "stream_url": "rtsp://admin:Camerite@186.226.193.111:601/h264/ch1/main/av_stream", "location": "Av. Amelia Fukuda - Navirai"},
    {"name": "LPR Av. Amambai - CAM 1", "stream_url": "rtsp://admin:Camerite@186.226.193.111:600/h264/ch1/main/av_stream", "location": "Av. Amambai - Navirai"},
    {"name": "LPR AV. Campo Grande - CAM 1", "stream_url": "rtsp://admin:Camerite@170.84.217.84:603/h264/ch1/main/av_stream", "location": "Av. Campo Grande - Navirai"},
    {"name": "LPR Av. Mato Grosso / Av. Porto Belo - CAM 1", "stream_url": "rtsp://admin:Camerite@170.84.217.83:608/h264/ch1/main/av_stream", "location": "Av. Mato Grosso - Navirai"},
    {"name": "LPR AV. Campo Grande - CAM 2 (FLEET NET)", "stream_url": "rtsp://admin:Camerite@170.84.217.71:608/h264/ch1/main/av_stream", "location": "Av. Campo Grande - Navirai"}
]

for cam in cameras:
    try:
        camera, created = Camera.objects.get_or_create(
            stream_url=cam["stream_url"],
            defaults={
                "name": cam["name"],
                "owner": admin,
                "location": cam["location"],
                "status": "online",
                "recording_enabled": True
            }
        )
        if created:
            print(f"OK - {cam['name']}")
        else:
            print(f"JA EXISTE - {cam['name']}")
    except Exception as e:
        print(f"ERRO - {cam['name']}: {str(e)[:50]}")

print(f"\nConcluido!")
