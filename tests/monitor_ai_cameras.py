import requests
import time

url = "http://localhost:5000/cameras"

for i in range(10):
    try:
        response = requests.get(url, timeout=2)
        data = response.json()
        print(f"[{i+1}/10] Active cameras: {len(data.get('cameras', []))}")
        for cam in data.get('cameras', []):
            print(f"  - Camera {cam['id']}: {cam['url']}")
    except Exception as e:
        print(f"Error: {e}")
    
    time.sleep(2)
