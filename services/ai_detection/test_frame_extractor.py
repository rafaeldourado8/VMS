import asyncio
import os
from infrastructure.frame_extractor import FrameExtractor

async def test_frame_extraction():
    rabbitmq_url = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
    
    # Exemplo: usar uma câmera de teste
    camera_id = "camera_1"
    rtsp_url = "rtsp://mediamtx:8554/camera/1"
    
    extractor = FrameExtractor(rabbitmq_url)
    await extractor.connect()
    
    print(f"Starting frame extraction for {camera_id}...")
    await extractor.extract_and_publish(camera_id, rtsp_url)
    
    await extractor.close()

if __name__ == "__main__":
    asyncio.run(test_frame_extraction())
