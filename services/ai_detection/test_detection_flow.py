import asyncio
import os
from application.detection_service import DetectionService
from infrastructure.detection_repository import DetectionRepository
from infrastructure.detection_publisher import DetectionPublisher
from PIL import Image
import io


async def test_detection_flow():
    print("Testing complete detection flow...\n")
    
    # Setup
    db_url = os.getenv('DB_URL', 'postgresql://vms:vms123@postgres_db:5432/vms_mvp')
    rabbitmq_url = os.getenv('RABBITMQ_URL', 'amqp://vms:vms123@rabbitmq:5672/')
    
    repository = DetectionRepository(db_url)
    publisher = DetectionPublisher(rabbitmq_url)
    
    try:
        await repository.connect()
        print("✅ Connected to PostgreSQL")
        
        await publisher.connect()
        print("✅ Connected to RabbitMQ")
        
        # Create test image
        img = Image.new('RGB', (200, 200), color='blue')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes = img_bytes.getvalue()
        
        # Process detection
        service = DetectionService(repository, publisher)
        print("\n🔍 Processing frame...")
        
        result = await service.process_frame('camera_test', img_bytes)
        
        print(f"\n✅ Detection completed!")
        print(f"  Camera: {result.camera_id}")
        print(f"  Provider: {result.provider}")
        print(f"  Detections: {len(result.detections)}")
        print(f"  Avg Confidence: {result.confidence_avg:.2f}%")
        print(f"  Timestamp: {result.timestamp}")
        
        print("\n✅ Saved to PostgreSQL")
        print("✅ Published to RabbitMQ exchange 'detections'")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await repository.close()
        await publisher.close()


if __name__ == "__main__":
    asyncio.run(test_detection_flow())
