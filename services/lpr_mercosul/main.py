"""LPR Mercosul Gateway - VMS Integration"""
import os
import cv2
import time
import uuid
import requests
from datetime import datetime, timedelta
from threading import Thread
from PIL import Image
import numpy as np
from ultralytics import YOLO
from dotenv import load_dotenv
from collections import Counter
import utils

# Load config
load_dotenv()
BACKEND_URL = os.getenv('BACKEND_URL', 'http://backend:8000')
ADMIN_API_KEY = os.getenv('ADMIN_API_KEY')
MEDIA_PATH = os.getenv('MEDIA_PATH', './media/detections')
VEHICLE_MODEL = os.getenv('VEHICLE_MODEL', 'yolov8n.pt')
PLATE_MODEL = os.getenv('PLATE_MODEL', 'models/tdiblik_lp_finetuned_yolov8n.pt')
FRAME_SKIP = int(os.getenv('FRAME_SKIP', '3'))
SKIP_Y_THRESHOLD = float(os.getenv('SKIP_Y_THRESHOLD', '100.0'))
VALIDATION_ROUNDS = int(os.getenv('VALIDATION_ROUNDS', '3'))
MIN_OCCURRENCES = int(os.getenv('MIN_OCCURRENCES', '2'))
MIN_CHARS = int(os.getenv('MIN_CHARS', '4'))

print("🔄 Loading models...")
print(f"Vehicle: {VEHICLE_MODEL}")
print(f"Plate: {PLATE_MODEL}")

# Load models (auto-download if not exists)
try:
    VEHICLE_YOLO = YOLO(VEHICLE_MODEL)
    print("✅ Vehicle model loaded")
except Exception as e:
    print(f"❌ Vehicle model error: {e}")
    exit(1)

try:
    PLATE_YOLO = YOLO(PLATE_MODEL)
    print("✅ Plate model loaded")
except Exception as e:
    print(f"❌ Plate model error: {e}")
    exit(1)

# Vehicle classes
CAR_LABELS = [
    utils.normalize_label('car'),
    utils.normalize_label('motorcycle'),
    utils.normalize_label('bus'),
    utils.normalize_label('truck')
]

# Create media dir
os.makedirs(MEDIA_PATH, exist_ok=True)


def get_active_cameras():
    """Fetch active RTSP cameras from backend"""
    try:
        response = requests.get(
            f'{BACKEND_URL}/api/cameras/lpr/active/',
            headers={'X-API-Key': ADMIN_API_KEY},
            params={'protocol': 'rtsp', 'is_active': 'true'},
            timeout=10
        )
        response.raise_for_status()
        return response.json().get('results', [])
    except Exception as e:
        print(f"❌ Error fetching cameras: {e}")
        return []


def detect_plates_in_frame(frame: Image, camera_id: int):
    """Detect license plates in frame"""
    num_vehicles, vehicle_boxes = utils.detect_with_yolo(VEHICLE_YOLO, frame, False)
    
    if num_vehicles == 0:
        return []
    
    detections = []
    
    for i, vehicle_box in enumerate(vehicle_boxes):
        # Check vehicle type
        label = utils.normalize_label(VEHICLE_YOLO.names[int(vehicle_box.cls)])
        if label not in CAR_LABELS:
            continue
        
        # Check distance
        x_min, y_min, x_max, y_max = vehicle_box.xyxy.cpu().detach().numpy()[0]
        if y_max < SKIP_Y_THRESHOLD:
            continue
        
        # Crop vehicle
        vehicle_img = frame.crop((x_min, y_min, x_max, y_max))
        
        # Detect plates
        num_plates, plate_boxes = utils.detect_with_yolo(PLATE_YOLO, vehicle_img, False)
        
        if num_plates == 0:
            continue
        
        for j, plate_box in enumerate(plate_boxes):
            plate_img, plate_text = utils.read_license_plate(plate_box, vehicle_img, MIN_CHARS)
            
            if len(plate_text) < MIN_CHARS:
                continue
            
            detections.append({
                'camera_id': camera_id,
                'plate': plate_text,
                'vehicle_img': vehicle_img,
                'plate_img': plate_img,
                'bbox': [int(x_min), int(y_min), int(x_max), int(y_max)]
            })
    
    return detections


def validate_detections(rounds):
    """Validate detections across multiple rounds"""
    if not rounds:
        return []
    
    # Count occurrences
    plate_counts = Counter()
    for detections in rounds:
        for det in detections:
            plate_counts[det['plate']] += 1
    
    # Filter valid
    validated = []
    seen = set()
    
    for detections in rounds:
        for det in detections:
            plate = det['plate']
            if plate_counts[plate] >= MIN_OCCURRENCES and plate not in seen:
                validated.append(det)
                seen.add(plate)
    
    return validated


def save_detection(detection):
    """Save detection images to media folder"""
    detection_id = str(uuid.uuid4())
    
    vehicle_path = os.path.join(MEDIA_PATH, f"{detection_id}_vehicle.jpg")
    plate_path = os.path.join(MEDIA_PATH, f"{detection_id}_plate.jpg")
    
    detection['vehicle_img'].save(vehicle_path, 'JPEG')
    detection['plate_img'].save(plate_path, 'JPEG')
    
    return detection_id, vehicle_path, plate_path


def send_to_backend(detection, detection_id, vehicle_path, plate_path):
    """Send detection to backend"""
    try:
        payload = {
            'camera_id': detection['camera_id'],
            'plate': detection['plate'],
            'confidence': 0.85,
            'timestamp': datetime.now().isoformat(),
            'image_url': vehicle_path
        }
        
        response = requests.post(
            f'{BACKEND_URL}/api/deteccoes/ingest/',
            headers={'X-API-Key': ADMIN_API_KEY},
            json=payload,
            timeout=10
        )
        response.raise_for_status()
        print(f"✅ Sent: {detection['plate']} (Camera {detection['camera_id']})")
    except Exception as e:
        print(f"❌ Error sending detection: {e}")
        print(f"Response: {response.text if 'response' in locals() else 'No response'}")


def process_camera(camera):
    """Process single camera stream"""
    camera_id = camera['id']
    rtsp_url = camera['rtsp_url']
    camera_name = camera['name']
    
    print(f"🎥 Processing: {camera_name} ({rtsp_url})")
    
    cap = cv2.VideoCapture(rtsp_url)
    frame_count = 0
    detection_buffer = []
    recent_plates = {}  # plate -> timestamp
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            print(f"🔄 Reconnecting: {camera_name}")
            cap.release()
            time.sleep(5)
            cap = cv2.VideoCapture(rtsp_url)
            continue
        
        frame_count += 1
        
        # Frame skip
        if frame_count % FRAME_SKIP != 0:
            continue
        
        # Convert to PIL
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_frame = Image.fromarray(rgb_frame)
        
        # Detect
        detections = detect_plates_in_frame(pil_frame, camera_id)
        detection_buffer.append(detections)
        
        # Validate when buffer full
        if len(detection_buffer) < VALIDATION_ROUNDS:
            continue
        
        validated = validate_detections(detection_buffer)
        detection_buffer.pop(0)
        
        if not validated:
            continue
        
        # Process validated detections
        current_time = datetime.now()
        
        # Cleanup old plates
        recent_plates = {
            plate: ts for plate, ts in recent_plates.items()
            if current_time - ts < timedelta(minutes=5)
        }
        
        for det in validated:
            plate = det['plate']
            
            # Check duplicates
            if plate in recent_plates:
                continue
            
            recent_plates[plate] = current_time
            
            # Save and send
            det_id, veh_path, plt_path = save_detection(det)
            send_to_backend(det, det_id, veh_path, plt_path)
    
    cap.release()


def main():
    print("🚗 LPR Mercosul Gateway Started")
    print(f"📡 Backend: {BACKEND_URL}")
    print(f"💾 Media: {MEDIA_PATH}")
    print(f"🎯 Validation: {MIN_OCCURRENCES}/{VALIDATION_ROUNDS} rounds")
    
    while True:
        cameras = get_active_cameras()
        print(f"📹 Active cameras: {len(cameras)}")
        
        threads = []
        for camera in cameras:
            t = Thread(target=process_camera, args=(camera,), daemon=True)
            t.start()
            threads.append(t)
        
        time.sleep(60)


if __name__ == '__main__':
    main()
