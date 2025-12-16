import requests
import base64
import time
import cv2
import numpy as np

API_URL = "http://localhost:8080"

def test_health():
    response = requests.get(f"{API_URL}/health")
    print("Health:", response.json())

def test_detect_base64():
    img = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.rectangle(img, (100, 100), (300, 300), (255, 255, 255), -1)
    
    _, buffer = cv2.imencode('.jpg', img)
    img_base64 = base64.b64encode(buffer).decode('utf-8')
    
    payload = {
        "camera_id": 1,
        "image_base64": img_base64
    }
    
    start = time.time()
    response = requests.post(f"{API_URL}/detect", json=payload)
    elapsed = (time.time() - start) * 1000
    
    print(f"Detection (sync): {elapsed:.2f}ms")
    print(response.json())

def test_detect_async():
    img = np.zeros((480, 640, 3), dtype=np.uint8)
    _, buffer = cv2.imencode('.jpg', img)
    img_base64 = base64.b64encode(buffer).decode('utf-8')
    
    payload = {"camera_id": 1, "image_base64": img_base64}
    
    response = requests.post(f"{API_URL}/detect/async", json=payload)
    task_id = response.json()["task_id"]
    print(f"Task ID: {task_id}")
    
    for _ in range(10):
        time.sleep(0.5)
        result = requests.get(f"{API_URL}/result/{task_id}")
        if result.status_code == 200:
            print("Result:", result.json())
            break

def test_upload():
    img = np.zeros((480, 640, 3), dtype=np.uint8)
    _, buffer = cv2.imencode('.jpg', img)
    
    files = {'file': ('test.jpg', buffer.tobytes(), 'image/jpeg')}
    response = requests.post(f"{API_URL}/detect/upload?camera_id=1", files=files)
    print("Upload:", response.json())

def load_test(n_requests=100):
    img = np.zeros((480, 640, 3), dtype=np.uint8)
    _, buffer = cv2.imencode('.jpg', img)
    img_base64 = base64.b64encode(buffer).decode('utf-8')
    
    payload = {"camera_id": 1, "image_base64": img_base64}
    
    times = []
    for i in range(n_requests):
        start = time.time()
        requests.post(f"{API_URL}/detect/async", json=payload)
        elapsed = (time.time() - start) * 1000
        times.append(elapsed)
        
        if (i + 1) % 10 == 0:
            print(f"Sent {i+1}/{n_requests} requests")
    
    print(f"\nLoad Test Results:")
    print(f"Total: {n_requests} requests")
    print(f"Avg: {np.mean(times):.2f}ms")
    print(f"Min: {np.min(times):.2f}ms")
    print(f"Max: {np.max(times):.2f}ms")
    print(f"P95: {np.percentile(times, 95):.2f}ms")

if __name__ == "__main__":
    print("=== Testing AI Service ===\n")
    
    test_health()
    print("\n" + "="*50 + "\n")
    
    test_detect_base64()
    print("\n" + "="*50 + "\n")
    
    test_detect_async()
    print("\n" + "="*50 + "\n")
    
    # test_upload()
    # print("\n" + "="*50 + "\n")
    
    # load_test(100)
