#!/usr/bin/env python3
"""
Script de teste de integração do AI Detection Service
"""
import requests
import time
import sys

API_URL = "http://localhost:5000"

def test_health():
    print("Testing /health endpoint...")
    try:
        response = requests.get(f"{API_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert 'status' in data
        assert data['status'] == 'ok'
        print("Health check passed")
        return True
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_start_camera():
    print("\nTesting /camera/start endpoint...")
    try:
        payload = {
            'camera_id': 999,
            'rtsp_url': 'rtsp://test:test@192.168.1.100:554/stream'
        }
        response = requests.post(f"{API_URL}/camera/start", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            assert data['status'] == 'started'
            assert data['camera_id'] == 999
            print("Camera start passed")
            return True
        else:
            print(f" Camera start returned {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"Camera start failed: {e}")
        return False

def test_list_cameras():
    print("\nTesting /cameras endpoint...")
    try:
        response = requests.get(f"{API_URL}/cameras")
        assert response.status_code == 200
        data = response.json()
        assert 'cameras' in data
        print(f"List cameras passed (found {len(data['cameras'])} cameras)")
        return True
    except Exception as e:
        print(f"List cameras failed: {e}")
        return False

def test_stop_camera():
    print("\nTesting /camera/stop endpoint...")
    try:
        payload = {'camera_id': 999}
        response = requests.post(f"{API_URL}/camera/stop", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            assert data['status'] == 'stopped'
            print("Camera stop passed")
            return True
        elif response.status_code == 404:
            print("Camera not found (expected if not started)")
            return True
        else:
            print(f"Camera stop failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"Camera stop failed: {e}")
        return False

def main():
    print("=" * 60)
    print("AI Detection Service - Integration Tests")
    print("=" * 60)
    
    results = []
    
    # Test 1: Health
    results.append(test_health())
    time.sleep(1)
    
    # Test 2: List cameras
    results.append(test_list_cameras())
    time.sleep(1)
    
    # Test 3: Start camera
    results.append(test_start_camera())
    time.sleep(2)
    
    # Test 4: List cameras again
    results.append(test_list_cameras())
    time.sleep(1)
    
    # Test 5: Stop camera
    results.append(test_stop_camera())
    time.sleep(1)
    
    print("\n" + "=" * 60)
    print(f"Results: {sum(results)}/{len(results)} tests passed")
    print("=" * 60)
    
    if all(results):
        print("All tests passed!")
        sys.exit(0)
    else:
        print(" Some tests failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
