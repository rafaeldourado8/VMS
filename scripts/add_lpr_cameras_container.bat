@echo off
echo Adicionando cameras LPR direto no container...
echo.

docker-compose exec -T backend python manage.py shell <<EOF
from apps.cameras.models import Camera

cameras = [
    {"name": "LPR AV. AREADO - CAMERA 1", "rtsp_url": "rtsp://admin:Camerite123@45.236.226.72:6048/cam/realmonitor?channel=1&subtype=0", "location": "Av. Areado"},
    {"name": "LPR BR 060 - CAMERA 1", "rtsp_url": "rtsp://admin:Camerite123@45.236.226.71:6047/cam/realmonitor?channel=1&subtype=0", "location": "BR 060"},
    {"name": "LPR MS 338 - Saida Para Ribas - CARGIL - CAM 2", "rtsp_url": "rtsp://admin:Camerite123@45.236.226.70:6045/cam/realmonitor?channel=1&subtype=0", "location": "MS 338 - Cargil"},
    {"name": "LPR MS 338 - Saida Para Ribas - CARGIL - CAM 1", "rtsp_url": "rtsp://admin:Camerite123@45.236.226.70:6044/cam/realmonitor?channel=1&subtype=0", "location": "MS 338 - Cargil"},
    {"name": "LPR Av Weimar G. Torres - CAM 2", "rtsp_url": "rtsp://admin:Camerite@186.226.193.111:602/h264/ch1/main/av_stream", "location": "Av. Weimar G. Torres - Navirai"},
    {"name": "LPR Av. Amelia Fukuda - EXPONAVI - CAM 1", "rtsp_url": "rtsp://admin:Camerite@186.226.193.111:601/h264/ch1/main/av_stream", "location": "Av. Amelia Fukuda - Navirai"},
    {"name": "LPR Av. Amambai - CAM 1", "rtsp_url": "rtsp://admin:Camerite@186.226.193.111:600/h264/ch1/main/av_stream", "location": "Av. Amambai - Navirai"},
    {"name": "LPR AV. Campo Grande - CAM 1", "rtsp_url": "rtsp://admin:Camerite@170.84.217.84:603/h264/ch1/main/av_stream", "location": "Av. Campo Grande - Navirai"},
    {"name": "LPR Av. Mato Grosso / Av. Porto Belo - CAM 1", "rtsp_url": "rtsp://admin:Camerite@170.84.217.83:608/h264/ch1/main/av_stream", "location": "Av. Mato Grosso - Navirai"},
    {"name": "LPR AV. Campo Grande - CAM 2 (FLEET NET)", "rtsp_url": "rtsp://admin:Camerite@170.84.217.71:608/h264/ch1/main/av_stream", "location": "Av. Campo Grande - Navirai"}
]

for cam in cameras:
    camera, created = Camera.objects.get_or_create(name=cam["name"], defaults={"rtsp_url": cam["rtsp_url"], "location": cam["location"], "status": "online", "recording_enabled": True})
    print(f"{'✅' if created else '⚠️'} {cam['name']}")

print("\n✅ Concluido!")
EOF

echo.
pause
