#!/usr/bin/env python3
"""
GT-Vision AI Service - Test Script
Tests all major endpoints and functionalities
"""

import base64
import json
import requests
import time
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8080"
TIMEOUT = 30

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def test_health():
    """Test health endpoint"""
    print_header("Testing Health Endpoint")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        response.raise_for_status()
        data = response.json()
        
        print("✅ Health check passed!")
        print(f"   Status: {data['status']}")
        print(f"   Queue Size: {data['queue_size']}")
        print(f"   Processed Total: {data['processed_total']}")
        print(f"   Active Workers: {data['active_workers']}")
        print(f"   Active Streams: {data['active_streams']}")
        print(f"   GPU Available: {data['gpu_available']}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_detect_sync(image_path=None):
    """Test synchronous detection"""
    print_header("Testing Synchronous Detection")
    
    # Create a dummy image if none provided
    if not image_path:
        import numpy as np
        import cv2
        
        # Create a simple test image
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(img, "TEST IMAGE", (50, 240), 
                   cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
        
        _, buffer = cv2.imencode('.jpg', img)
        image_bytes = buffer.tobytes()
    else:
        with open(image_path, 'rb') as f:
            image_bytes = f.read()
    
    image_b64 = base64.b64encode(image_bytes).decode('utf-8')
    
    try:
        response = requests.post(
            f"{BASE_URL}/detect",
            json={
                "camera_id": 1,
                "image_base64": image_b64
            },
            timeout=TIMEOUT
        )
        response.raise_for_status()
        data = response.json()
        
        print("✅ Synchronous detection successful!")
        print(f"   Detections: {len(data['detections'])}")
        print(f"   Processing Time: {data['processing_time_ms']:.2f}ms")
        
        for i, det in enumerate(data['detections']):
            print(f"\n   Detection {i+1}:")
            print(f"     Type: {det['object_type']}")
            print(f"     Confidence: {det['confidence']:.3f}")
            if det.get('plate_number'):
                print(f"     Plate: {det['plate_number']}")
        
        return True
    except Exception as e:
        print(f"❌ Synchronous detection failed: {e}")
        return False

def test_detect_async(image_path=None):
    """Test asynchronous detection"""
    print_header("Testing Asynchronous Detection")
    
    # Create a dummy image if none provided
    if not image_path:
        import numpy as np
        import cv2
        
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        _, buffer = cv2.imencode('.jpg', img)
        image_bytes = buffer.tobytes()
    else:
        with open(image_path, 'rb') as f:
            image_bytes = f.read()
    
    image_b64 = base64.b64encode(image_bytes).decode('utf-8')
    
    try:
        # Submit task
        response = requests.post(
            f"{BASE_URL}/detect/async",
            json={
                "camera_id": 1,
                "image_base64": image_b64
            },
            timeout=TIMEOUT
        )
        response.raise_for_status()
        data = response.json()
        task_id = data['task_id']
        
        print(f"✅ Task submitted: {task_id}")
        print("   Waiting for result...")
        
        # Poll for result
        for i in range(50):
            time.sleep(0.1)
            result_response = requests.get(
                f"{BASE_URL}/result/{task_id}",
                timeout=5
            )
            
            if result_response.status_code == 200:
                result = result_response.json()
                print(f"✅ Result retrieved!")
                print(f"   Detections: {len(result['detections'])}")
                print(f"   Processing Time: {result['processing_time_ms']:.2f}ms")
                return True
        
        print("❌ Timeout waiting for result")
        return False
        
    except Exception as e:
        print(f"❌ Asynchronous detection failed: {e}")
        return False

def test_webhook():
    """Test webhook endpoint"""
    print_header("Testing Webhook Endpoint")
    
    webhook_data = {
        "Plate": {
            "PlateNumber": "ABC1234",
            "Confidence": 0.95
        },
        "Channel": 1,
        "DeviceName": "Test Camera"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/lpr-webhook",
            json=webhook_data,
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        print("✅ Webhook processed successfully!")
        print(f"   Status: {data['status']}")
        print(f"   Message: {data['message']}")
        return True
    except Exception as e:
        print(f"❌ Webhook test failed: {e}")
        return False

def test_stats():
    """Test statistics endpoints"""
    print_header("Testing Statistics Endpoints")
    
    try:
        # Test all stats
        response = requests.get(f"{BASE_URL}/stats/all", timeout=5)
        response.raise_for_status()
        data = response.json()
        
        print("✅ Statistics retrieved!")
        print(f"   Queue Size: {data['queue_size']}")
        print(f"   Task Workers: {data['total_task_workers']}")
        print(f"   Stream Workers: {data['total_stream_workers']}")
        return True
    except Exception as e:
        print(f"❌ Statistics test failed: {e}")
        return False

def test_metrics():
    """Test Prometheus metrics"""
    print_header("Testing Prometheus Metrics")
    
    try:
        response = requests.get(f"{BASE_URL}/metrics", timeout=5)
        response.raise_for_status()
        
        print("✅ Metrics endpoint accessible!")
        print(f"   Response length: {len(response.text)} bytes")
        
        # Count metrics
        metrics = [line for line in response.text.split('\n') 
                  if line and not line.startswith('#')]
        print(f"   Metrics available: {len(metrics)}")
        return True
    except Exception as e:
        print(f"❌ Metrics test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("  GT-Vision AI Service - Test Suite")
    print("="*60)
    
    tests = [
        ("Health Check", test_health),
        ("Synchronous Detection", test_detect_sync),
        ("Asynchronous Detection", test_detect_async),
        ("Webhook", test_webhook),
        ("Statistics", test_stats),
        ("Metrics", test_metrics)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Test '{name}' crashed: {e}")
            results.append((name, False))
        time.sleep(1)
    
    # Summary
    print_header("Test Summary")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    exit(main())
