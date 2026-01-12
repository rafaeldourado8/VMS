#!/usr/bin/env python3
"""Test Protocol Failover with Real Cameras"""

import requests
import time
import json

BACKEND_URL = "http://localhost:8000"

CAMERAS = [
    {
        "id": 1,
        "name": "Camera RTSP 1",
        "rtsp_url": "rtsp://admin:Camerite123@45.236.226.75:6052/cam/realmonitor?channel=1&subtype=0",
        "location": "Test Location 1"
    },
    {
        "id": 2,
        "name": "Camera RTSP 2",
        "rtsp_url": "rtsp://admin:Camerite@170.84.217.84:603/h264/ch1/main/av_stream",
        "location": "Test Location 2"
    },
    {
        "id": 3,
        "name": "Camera RTMP",
        "rtsp_url": "rtmp://inst-czd17-srs-rtmp-hik-pro-connect.camerite.services:1935/record/FC2487237.stream",
        "location": "Test Location 3"
    }
]

def provision_camera(camera):
    """Provision camera in backend"""
    print(f"  -> Provisioning: {camera['name']}")
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/cameras/",
            json={
                "name": camera["name"],
                "rtsp_url": camera["rtsp_url"],
                "location": camera["location"],
                "status": "online"
            },
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            print(f"     OK Success")
            return True
        else:
            print(f"     WARN Status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"     ERROR: {e}")
        return False

def check_stream(camera_id):
    """Check stream status"""
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/cameras/{camera_id}/stream",
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"     Stream URL: {data.get('stream_url', 'N/A')}")
            return True
        else:
            print(f"     Status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"     Error: {e}")
        return False

def main():
    print("Testing Protocol Failover")
    print("=" * 50)
    print()
    
    # Provision cameras
    print("Provisioning cameras...")
    for camera in CAMERAS:
        provision_camera(camera)
    
    print()
    print("Waiting 10s for streams to initialize...")
    time.sleep(10)
    
    # Check streams
    print()
    print("Checking stream status...")
    for camera in CAMERAS:
        print(f"  -> Camera {camera['id']}: {camera['name']}")
        check_stream(camera["id"])
    
    print()
    print("Test complete!")
    print()
    print("Next steps:")
    print("  1. Open frontend: http://localhost:5173")
    print("  2. Navigate to Mosaicos page")
    print("  3. Create mosaic with test cameras")
    print("  4. Observe protocol indicators in video player")
    print("  5. Check browser DevTools console for protocol switches")
    print("  6. Verify metrics endpoint for fallback counts")

if __name__ == "__main__":
    main()
