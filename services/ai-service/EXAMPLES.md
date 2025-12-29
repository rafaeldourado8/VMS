# GT-Vision AI Service - Usage Examples

## 📸 Basic Detection

### Python Example - Detect from Image File

```python
import requests
import base64
from pathlib import Path

def detect_from_file(image_path, camera_id=1):
    """Detect vehicles and plates from image file"""
    
    # Read and encode image
    with open(image_path, 'rb') as f:
        image_bytes = f.read()
    image_b64 = base64.b64encode(image_bytes).decode('utf-8')
    
    # Send request
    response = requests.post(
        'http://localhost:8080/detect',
        json={
            'camera_id': camera_id,
            'image_base64': image_b64
        },
        timeout=30
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"Found {len(data['detections'])} detections")
        
        for det in data['detections']:
            print(f"\n{det['object_type'].upper()}")
            print(f"  Confidence: {det['confidence']:.2%}")
            
            if det.get('plate_number'):
                print(f"  Plate: {det['plate_number']}")
                print(f"  Plate Confidence: {det['plate_confidence']:.2%}")
        
        return data
    else:
        print(f"Error: {response.status_code}")
        return None

# Usage
result = detect_from_file('car_image.jpg', camera_id=1)
```

### Python Example - Detect from OpenCV Frame

```python
import cv2
import requests
import base64

def detect_from_frame(frame, camera_id=1):
    """Detect from OpenCV frame"""
    
    # Encode frame to JPEG
    _, buffer = cv2.imencode('.jpg', frame)
    image_b64 = base64.b64encode(buffer).decode('utf-8')
    
    # Send request
    response = requests.post(
        'http://localhost:8080/detect',
        json={
            'camera_id': camera_id,
            'image_base64': image_b64
        }
    )
    
    return response.json() if response.ok else None

# Usage with webcam
cap = cv2.VideoCapture(0)
ret, frame = cap.read()
if ret:
    detections = detect_from_frame(frame)
    print(detections)
cap.release()
```

---

## 🔄 Asynchronous Detection

### Python Example - Async Queue

```python
import requests
import time

def detect_async(image_path, camera_id=1):
    """Submit async detection task"""
    
    with open(image_path, 'rb') as f:
        image_bytes = f.read()
    image_b64 = base64.b64encode(image_bytes).decode('utf-8')
    
    # Submit task
    response = requests.post(
        'http://localhost:8080/detect/async',
        json={
            'camera_id': camera_id,
            'image_base64': image_b64
        }
    )
    
    if response.status_code == 200:
        task_id = response.json()['task_id']
        print(f"Task submitted: {task_id}")
        
        # Poll for result
        for _ in range(50):
            result = requests.get(f'http://localhost:8080/result/{task_id}')
            if result.status_code == 200:
                return result.json()
            time.sleep(0.1)
        
        print("Timeout waiting for result")
    
    return None

# Usage
result = detect_async('car_image.jpg')
```

---

## 🎥 Batch Processing

### Python Example - Process Multiple Images

```python
import requests
import base64
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import time

def process_image(image_path):
    """Process single image"""
    with open(image_path, 'rb') as f:
        image_b64 = base64.b64encode(f.read()).decode('utf-8')
    
    response = requests.post(
        'http://localhost:8080/detect/async',
        json={'camera_id': 1, 'image_base64': image_b64}
    )
    
    if response.ok:
        return response.json()['task_id']
    return None

def get_result(task_id, max_attempts=50):
    """Poll for result"""
    for _ in range(max_attempts):
        response = requests.get(f'http://localhost:8080/result/{task_id}')
        if response.ok:
            return response.json()
        time.sleep(0.1)
    return None

def batch_process(image_dir):
    """Process all images in directory"""
    images = list(Path(image_dir).glob('*.jpg'))
    
    # Submit all tasks
    with ThreadPoolExecutor(max_workers=10) as executor:
        task_ids = list(executor.map(process_image, images))
    
    # Collect results
    results = []
    for task_id in task_ids:
        if task_id:
            result = get_result(task_id)
            if result:
                results.append(result)
    
    return results

# Usage
results = batch_process('/path/to/images/')
print(f"Processed {len(results)} images")
```

---

## 📹 Video Processing

### Python Example - Process Video File

```python
import cv2
import requests
import base64

def process_video(video_path, frame_skip=5):
    """Process video file"""
    
    cap = cv2.VideoCapture(video_path)
    frame_count = 0
    detections_all = []
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        
        # Skip frames for optimization
        if frame_count % frame_skip != 0:
            continue
        
        # Encode and detect
        _, buffer = cv2.imencode('.jpg', frame)
        image_b64 = base64.b64encode(buffer).decode('utf-8')
        
        try:
            response = requests.post(
                'http://localhost:8080/detect',
                json={'camera_id': 1, 'image_base64': image_b64},
                timeout=5
            )
            
            if response.ok:
                data = response.json()
                
                # Filter only detections with plates
                plates = [d for d in data['detections'] if d.get('plate_number')]
                
                if plates:
                    print(f"Frame {frame_count}: Found {len(plates)} plates")
                    for p in plates:
                        print(f"  - {p['plate_number']}")
                    
                    detections_all.extend(plates)
        
        except Exception as e:
            print(f"Error on frame {frame_count}: {e}")
    
    cap.release()
    return detections_all

# Usage
plates = process_video('parking_lot.mp4', frame_skip=10)
print(f"\nTotal unique plates: {len(set(p['plate_number'] for p in plates))}")
```

---

## 🌐 Webhook Integration

### Example - External LPR Camera Webhook

```python
import requests

def send_lpr_webhook(plate_number, camera_id, confidence=0.95):
    """Simulate external LPR camera webhook"""
    
    webhook_data = {
        "Plate": {
            "PlateNumber": plate_number,
            "Confidence": confidence
        },
        "Channel": camera_id,
        "DeviceName": f"External LPR {camera_id}",
        "CaptureTime": "2024-01-15T10:30:00Z"
    }
    
    response = requests.post(
        'http://localhost:8080/lpr-webhook',
        json=webhook_data,
        timeout=10
    )
    
    return response.json() if response.ok else None

# Usage
result = send_lpr_webhook("ABC1234", camera_id=5)
print(result)
```

### Example - Webhook Server (Receive from Camera)

```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/camera-webhook', methods=['POST'])
def camera_webhook():
    """Receive webhook from camera and forward to AI service"""
    
    data = request.json
    
    # Forward to AI service
    response = requests.post(
        'http://localhost:8080/lpr-webhook',
        json=data
    )
    
    return jsonify({"status": "forwarded"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
```

---

## 📊 Monitoring Integration

### Python Example - Collect Metrics

```python
import requests
from prometheus_client.parser import text_string_to_metric_families

def get_metrics():
    """Parse Prometheus metrics"""
    
    response = requests.get('http://localhost:8080/metrics')
    
    metrics = {}
    for family in text_string_to_metric_families(response.text):
        for sample in family.samples:
            metrics[sample.name] = sample.value
    
    return metrics

# Usage
metrics = get_metrics()
print(f"Total detections: {metrics.get('detections_processed_total', 0)}")
print(f"Queue size: {metrics.get('detection_queue_size', 0)}")
```

### Python Example - Health Check Monitor

```python
import requests
import time

def monitor_health(interval=30):
    """Continuously monitor service health"""
    
    while True:
        try:
            response = requests.get('http://localhost:8080/health', timeout=5)
            
            if response.ok:
                data = response.json()
                print(f"[{time.strftime('%H:%M:%S')}] Status: {data['status']}")
                print(f"  Queue: {data['queue_size']}")
                print(f"  Processed: {data['processed_total']}")
                print(f"  Avg Time: {data['avg_processing_time_ms']:.2f}ms")
            else:
                print(f"[{time.strftime('%H:%M:%S')}] Service unhealthy!")
        
        except Exception as e:
            print(f"[{time.strftime('%H:%M:%S')}] Error: {e}")
        
        time.sleep(interval)

# Usage
monitor_health(interval=60)
```

---

## 🔗 Integration with Django Backend

### Python Example - Full Integration

```python
import requests
import base64

class GTVisionClient:
    """Complete client for GT-Vision integration"""
    
    def __init__(self, ai_url='http://localhost:8080', 
                 backend_url='http://localhost:8000',
                 api_key=None):
        self.ai_url = ai_url
        self.backend_url = backend_url
        self.headers = {'X-API-Key': api_key} if api_key else {}
    
    def detect_and_save(self, image_path, camera_id):
        """Detect plate and save to backend"""
        
        # 1. Detect with AI service
        with open(image_path, 'rb') as f:
            image_b64 = base64.b64encode(f.read()).decode('utf-8')
        
        response = requests.post(
            f'{self.ai_url}/detect',
            json={'camera_id': camera_id, 'image_base64': image_b64}
        )
        
        if not response.ok:
            return None
        
        data = response.json()
        
        # 2. Send plates to backend
        results = []
        for detection in data['detections']:
            if detection.get('plate_number'):
                result = self._send_to_backend(detection)
                results.append(result)
        
        return results
    
    def _send_to_backend(self, detection):
        """Send detection to Django backend"""
        
        payload = {
            'license_plate': detection['plate_number'],
            'camera_id': detection['camera_id'],
            'confidence': detection.get('plate_confidence', 0.0),
            'image_path': detection.get('image_path', '')
        }
        
        response = requests.post(
            f'{self.backend_url}/api/v1/internal/sightings',
            json=payload,
            headers=self.headers
        )
        
        return response.json() if response.ok else None

# Usage
client = GTVisionClient(api_key='your-api-key')
results = client.detect_and_save('car.jpg', camera_id=1)
print(results)
```

---

## 🚀 Performance Testing

### Python Example - Load Test

```python
import requests
import base64
import time
from concurrent.futures import ThreadPoolExecutor
import numpy as np

def generate_test_image():
    """Generate random test image"""
    import cv2
    img = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    _, buffer = cv2.imencode('.jpg', img)
    return base64.b64encode(buffer).decode('utf-8')

def single_request(request_id):
    """Single detection request"""
    start = time.time()
    
    try:
        response = requests.post(
            'http://localhost:8080/detect/async',
            json={
                'camera_id': 1,
                'image_base64': generate_test_image()
            },
            timeout=10
        )
        
        duration = time.time() - start
        return {
            'id': request_id,
            'success': response.ok,
            'duration': duration
        }
    except Exception as e:
        return {
            'id': request_id,
            'success': False,
            'error': str(e)
        }

def load_test(num_requests=100, workers=10):
    """Run load test"""
    
    print(f"Starting load test: {num_requests} requests, {workers} workers")
    start = time.time()
    
    with ThreadPoolExecutor(max_workers=workers) as executor:
        results = list(executor.map(single_request, range(num_requests)))
    
    duration = time.time() - start
    
    # Statistics
    successful = sum(1 for r in results if r['success'])
    avg_duration = np.mean([r['duration'] for r in results if 'duration' in r])
    
    print(f"\nResults:")
    print(f"  Total requests: {num_requests}")
    print(f"  Successful: {successful}")
    print(f"  Failed: {num_requests - successful}")
    print(f"  Total time: {duration:.2f}s")
    print(f"  Requests/sec: {num_requests/duration:.2f}")
    print(f"  Avg latency: {avg_duration*1000:.2f}ms")

# Usage
load_test(num_requests=100, workers=10)
```

---

**Examples v2.0**
