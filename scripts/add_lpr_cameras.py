import requests
import sys

API_URL = "http://localhost/api/cameras/"
USERNAME = "admin"
PASSWORD = "admin"

cameras = [
    {
        "name": "LPR AV. AREADO - CAMERA 1",
        "rtsp_url": "rtsp://admin:Camerite123@45.236.226.72:6048/cam/realmonitor?channel=1&subtype=0",
        "location": "Av. Areado"
    },
    {
        "name": "LPR BR 060 - CAMERA 1",
        "rtsp_url": "rtsp://admin:Camerite123@45.236.226.71:6047/cam/realmonitor?channel=1&subtype=0",
        "location": "BR 060"
    },
    {
        "name": "LPR MS 338 - Saida Para Ribas - CARGIL - CAM 2",
        "rtsp_url": "rtsp://admin:Camerite123@45.236.226.70:6045/cam/realmonitor?channel=1&subtype=0",
        "location": "MS 338 - Cargil"
    },
    {
        "name": "LPR MS 338 - Saida Para Ribas - CARGIL - CAM 1",
        "rtsp_url": "rtsp://admin:Camerite123@45.236.226.70:6044/cam/realmonitor?channel=1&subtype=0",
        "location": "MS 338 - Cargil"
    },
    {
        "name": "LPR Av Weimar G. Torres - CAM 2",
        "rtsp_url": "rtsp://admin:Camerite@186.226.193.111:602/h264/ch1/main/av_stream",
        "location": "Av. Weimar G. Torres - Navirai"
    },
    {
        "name": "LPR Av. Amélia Fukuda - EXPONAVI - CAM 1",
        "rtsp_url": "rtsp://admin:Camerite@186.226.193.111:601/h264/ch1/main/av_stream",
        "location": "Av. Amélia Fukuda - Navirai"
    },
    {
        "name": "LPR Av. Amambai - CAM 1",
        "rtsp_url": "rtsp://admin:Camerite@186.226.193.111:600/h264/ch1/main/av_stream",
        "location": "Av. Amambai - Navirai"
    },
    {
        "name": "LPR AV. Campo Grande - CAM 1",
        "rtsp_url": "rtsp://admin:Camerite@170.84.217.84:603/h264/ch1/main/av_stream",
        "location": "Av. Campo Grande - Navirai"
    },
    {
        "name": "LPR Av. Mato Grosso / Av. Porto Belo - CAM 1",
        "rtsp_url": "rtsp://admin:Camerite@170.84.217.83:608/h264/ch1/main/av_stream",
        "location": "Av. Mato Grosso - Navirai"
    },
    {
        "name": "LPR AV. Campo Grande - CAM 2 (FLEET NET)",
        "rtsp_url": "rtsp://admin:Camerite@170.84.217.71:608/h264/ch1/main/av_stream",
        "location": "Av. Campo Grande - Navirai"
    }
]

def add_camera(camera):
    data = {
        "name": camera["name"],
        "rtsp_url": camera["rtsp_url"],
        "location": camera["location"],
        "status": "online",
        "recording_enabled": True
    }
    
    try:
        response = requests.post(
            API_URL,
            json=data,
            auth=(USERNAME, PASSWORD),
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            print(f"✅ {camera['name']}")
            return True
        else:
            print(f"❌ {camera['name']}: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ {camera['name']}: {e}")
        return False

if __name__ == "__main__":
    print(f"Adicionando {len(cameras)} câmeras LPR...\n")
    
    success = 0
    for camera in cameras:
        if add_camera(camera):
            success += 1
    
    print(f"\n✅ {success}/{len(cameras)} câmeras adicionadas com sucesso")
