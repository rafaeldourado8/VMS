import asyncio
import aiohttp
import base64
import time
import numpy as np
import cv2
from statistics import mean, stdev

API_URL = "http://localhost:8080"
N_CAMERAS = 250
N_FRAMES_PER_CAMERA = 10

async def send_detection(session, camera_id, img_base64):
    payload = {"camera_id": camera_id, "image_base64": img_base64}
    start = time.time()
    
    async with session.post(f"{API_URL}/detect/async", json=payload) as resp:
        result = await resp.json()
        elapsed = (time.time() - start) * 1000
        return elapsed, result

async def benchmark():
    img = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.rectangle(img, (100, 100), (300, 300), (255, 255, 255), -1)
    _, buffer = cv2.imencode('.jpg', img)
    img_base64 = base64.b64encode(buffer).decode('utf-8')
    
    async with aiohttp.ClientSession() as session:
        print(f"Simulating {N_CAMERAS} cameras, {N_FRAMES_PER_CAMERA} frames each")
        print(f"Total requests: {N_CAMERAS * N_FRAMES_PER_CAMERA}\n")
        
        start_time = time.time()
        tasks = []
        
        for camera_id in range(1, N_CAMERAS + 1):
            for _ in range(N_FRAMES_PER_CAMERA):
                tasks.append(send_detection(session, camera_id, img_base64))
        
        results = await asyncio.gather(*tasks)
        
        total_time = time.time() - start_time
        latencies = [r[0] for r in results]
        
        print(f"Total time: {total_time:.2f}s")
        print(f"Throughput: {len(results)/total_time:.2f} req/s")
        print(f"\nLatency stats:")
        print(f"  Mean: {mean(latencies):.2f}ms")
        print(f"  Stdev: {stdev(latencies):.2f}ms")
        print(f"  Min: {min(latencies):.2f}ms")
        print(f"  Max: {max(latencies):.2f}ms")
        print(f"  P50: {np.percentile(latencies, 50):.2f}ms")
        print(f"  P95: {np.percentile(latencies, 95):.2f}ms")
        print(f"  P99: {np.percentile(latencies, 99):.2f}ms")

if __name__ == "__main__":
    asyncio.run(benchmark())
