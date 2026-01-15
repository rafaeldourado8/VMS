"""Test LPR Mercosul Integration"""
import requests
import time

BACKEND_URL = "http://localhost:8000"
ADMIN_API_KEY = "GtVisionAdmin2025"

def test_cameras_endpoint():
    """Test if LPR can fetch cameras"""
    print("🧪 Testing cameras endpoint...")
    
    response = requests.get(
        f'{BACKEND_URL}/api/cameras/lpr/active/',
        headers={'X-API-Key': ADMIN_API_KEY},
        params={'protocol': 'rtsp', 'is_active': 'true'}
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert 'results' in data, "Missing 'results' key"
    
    print(f"✅ Found {len(data['results'])} cameras")
    return data['results']


def test_detection_endpoint():
    """Test if LPR can send detections"""
    print("\n🧪 Testing detection endpoint...")
    
    payload = {
        'camera_id': 1,
        'plate': 'ABC1234',
        'confidence': 0.95,
        'timestamp': '2026-01-15T12:00:00',
        'image_url': '/media/test.jpg'
    }
    
    response = requests.post(
        f'{BACKEND_URL}/api/deteccoes/ingest/',
        headers={'X-API-Key': ADMIN_API_KEY},
        json=payload
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 201:
        print("✅ Detection sent successfully")
        return True
    else:
        print(f"❌ Failed: {response.status_code}")
        return False


def test_mediamtx_status():
    """Test MediaMTX health"""
    print("\n🧪 Testing MediaMTX...")
    
    try:
        response = requests.get('http://localhost:9997/v3/config/global/get', timeout=5)
        print(f"✅ MediaMTX is running (Status: {response.status_code})")
        return True
    except Exception as e:
        print(f"❌ MediaMTX error: {e}")
        return False


if __name__ == '__main__':
    print("=" * 60)
    print("LPR MERCOSUL INTEGRATION TEST")
    print("=" * 60)
    
    # Test 1: Cameras
    try:
        cameras = test_cameras_endpoint()
    except Exception as e:
        print(f"❌ Camera test failed: {e}")
        cameras = []
    
    # Test 2: Detection
    try:
        test_detection_endpoint()
    except Exception as e:
        print(f"❌ Detection test failed: {e}")
    
    # Test 3: MediaMTX
    test_mediamtx_status()
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
