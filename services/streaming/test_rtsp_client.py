import asyncio
import sys
from infrastructure.rtsp_client import RTSPClient
from infrastructure.mediamtx.mediamtx_client import MediaMTXClient

async def test_rtsp_client():
    """Test RTSPClient with mock camera"""
    
    # Setup
    mediamtx = MediaMTXClient(base_url="http://localhost:9997")
    client = RTSPClient(
        camera_id="test_camera_1",
        rtsp_url="rtsp://invalid-url-for-testing:554/stream",
        mediamtx_client=mediamtx
    )
    
    print("[TEST] Testing RTSPClient...")
    print(f"Camera: {client.camera_id}")
    print(f"RTSP URL: {client.rtsp_url}")
    print(f"Max retries: {client.MAX_RETRIES}")
    print(f"Backoff intervals: {client.BACKOFF_INTERVALS}")
    print()
    
    # Test 1: Connection with retry
    print("Test 1: Connection with exponential backoff")
    print("-" * 50)
    success = await client.connect_with_retry()
    print(f"Result: {'[OK] Connected' if success else '[FAIL] Failed after retries'}")
    print(f"Status: {'[ONLINE]' if client.is_online else '[OFFLINE]'}")
    print()
    
    # Test 2: Health check (run for 10 seconds)
    if success:
        print("Test 2: Health check loop (10s)")
        print("-" * 50)
        client.start_health_check()
        await asyncio.sleep(10)
        client.stop_health_check()
        print("[OK] Health check completed")
    
    print()
    print("[DONE] Test finished")

if __name__ == "__main__":
    try:
        asyncio.run(test_rtsp_client())
    except KeyboardInterrupt:
        print("\n[WARN] Test interrupted")
        sys.exit(0)
