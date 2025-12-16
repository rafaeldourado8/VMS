import cv2
import requests
import base64
import time
from datetime import datetime
from collections import defaultdict

API_URL = "http://localhost:8080"

CAMERAS = [
    {"id": 1, "url": "rtsp://admin:Camerite123@45.236.226.75:6053/cam/realmonitor?channel=1&subtype=0"},
    {"id": 2, "url": "rtsp://admin:Camerite123@45.236.226.75:6052/cam/realmonitor?channel=1&subtype=0"},
    {"id": 3, "url": "rtsp://admin:Camerite123@45.236.226.74:6050/cam/realmonitor?channel=1&subtype=0"},
    {"id": 4, "url": "rtsp://admin:Camerite123@45.236.226.72:6049/cam/realmonitor?channel=1&subtype=0"},
]

DURATION_SECONDS = 60
FRAMES_PER_CAMERA = 10

def capture_and_detect(camera_id, rtsp_url):
    cap = cv2.VideoCapture(rtsp_url)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        return None
    
    _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
    img_base64 = base64.b64encode(buffer).decode('utf-8')
    
    try:
        response = requests.post(
            f"{API_URL}/detect/async",
            json={"camera_id": camera_id, "image_base64": img_base64},
            timeout=5
        )
        return response.json()["task_id"]
    except:
        return None

def get_result(task_id):
    try:
        response = requests.get(f"{API_URL}/result/{task_id}", timeout=2)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

def continuous_test():
    print(f"\n{'='*70}")
    print(f"TESTE CONTÍNUO - {DURATION_SECONDS}s - {FRAMES_PER_CAMERA} frames/câmera")
    print(f"{'='*70}\n")
    
    stats = defaultdict(lambda: {"total": 0, "detections": 0, "objects": defaultdict(int)})
    pending_tasks = {}
    
    start_time = time.time()
    frame_count = 0
    
    while time.time() - start_time < DURATION_SECONDS:
        for camera in CAMERAS:
            if stats[camera['id']]["total"] >= FRAMES_PER_CAMERA:
                continue
            
            task_id = capture_and_detect(camera['id'], camera['url'])
            if task_id:
                pending_tasks[task_id] = {"camera_id": camera['id'], "time": time.time()}
                stats[camera['id']]["total"] += 1
                frame_count += 1
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Cam {camera['id']}: Frame {stats[camera['id']]['total']}/{FRAMES_PER_CAMERA} enviado")
        
        # Check results
        for task_id in list(pending_tasks.keys()):
            result = get_result(task_id)
            if result:
                camera_id = pending_tasks[task_id]["camera_id"]
                detections = result.get("detections", [])
                
                if detections:
                    stats[camera_id]["detections"] += len(detections)
                    for det in detections:
                        stats[camera_id]["objects"][det["object_type"]] += 1
                
                del pending_tasks[task_id]
        
        time.sleep(0.5)
    
    # Wait for remaining results
    print("\nAguardando resultados pendentes...")
    timeout = time.time() + 10
    while pending_tasks and time.time() < timeout:
        for task_id in list(pending_tasks.keys()):
            result = get_result(task_id)
            if result:
                camera_id = pending_tasks[task_id]["camera_id"]
                detections = result.get("detections", [])
                
                if detections:
                    stats[camera_id]["detections"] += len(detections)
                    for det in detections:
                        stats[camera_id]["objects"][det["object_type"]] += 1
                
                del pending_tasks[task_id]
        time.sleep(0.5)
    
    # Print results
    print(f"\n{'='*70}")
    print("RESULTADOS")
    print(f"{'='*70}\n")
    
    total_frames = sum(s["total"] for s in stats.values())
    total_detections = sum(s["detections"] for s in stats.values())
    
    for camera in CAMERAS:
        cam_stats = stats[camera['id']]
        print(f"Câmera {camera['id']}:")
        print(f"  Frames processados: {cam_stats['total']}")
        print(f"  Detecções totais: {cam_stats['detections']}")
        
        if cam_stats['objects']:
            print(f"  Objetos detectados:")
            for obj_type, count in cam_stats['objects'].items():
                print(f"    - {obj_type}: {count}")
        else:
            print(f"  Nenhum objeto detectado")
        print()
    
    print(f"{'='*70}")
    print(f"TOTAL: {total_frames} frames | {total_detections} detecções")
    print(f"Taxa de detecção: {(total_detections/total_frames*100) if total_frames > 0 else 0:.1f}%")
    print(f"{'='*70}\n")

if __name__ == "__main__":
    continuous_test()
