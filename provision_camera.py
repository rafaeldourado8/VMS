import requests

response = requests.post(
    "http://localhost:8001/cameras/provision",
    json={
        "camera_id": 2,
        "rtsp_url": "rtsp://admin:Camerite123@45.236.226.71:6047/cam/realmonitor?channel=1&subtype=0",
        "name": "rafael_gtvision_Teste 0",
        "on_demand": True
    }
)

print(response.status_code)
print(response.json())
