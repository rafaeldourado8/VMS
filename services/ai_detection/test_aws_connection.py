import asyncio
import os
from infrastructure.providers.rekognition import RekognitionProvider
from PIL import Image
import io


async def test_aws_connection():
    print("Testing AWS Rekognition connection...\n")
    
    # Check credentials
    access_key = os.getenv('AWS_ACCESS_KEY_ID', 'NOT_SET')
    region = os.getenv('AWS_REGION', 'us-east-1')
    
    print(f"AWS_ACCESS_KEY_ID: {access_key[:10]}..." if access_key != 'NOT_SET' else "AWS_ACCESS_KEY_ID: NOT_SET")
    print(f"AWS_REGION: {region}\n")
    
    if access_key == 'NOT_SET' or access_key == 'your_access_key':
        print("❌ AWS credentials not configured in .env file")
        print("\nUpdate .env with:")
        print("  AWS_ACCESS_KEY_ID=your_actual_key")
        print("  AWS_SECRET_ACCESS_KEY=your_actual_secret")
        print("  AWS_REGION=us-east-1")
        return
    
    # Create test image (simple red square)
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes = img_bytes.getvalue()
    
    provider = RekognitionProvider()
    
    try:
        print("Testing DetectLabels...")
        labels = await provider.detect_labels(img_bytes)
        print(f"✅ DetectLabels successful: {len(labels)} labels")
        
        print("\nTesting DetectFaces...")
        faces = await provider.detect_faces(img_bytes)
        print(f"✅ DetectFaces successful: {len(faces)} faces")
        
        print("\n✅ AWS Rekognition connection working!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nCheck:")
        print("  1. AWS credentials are correct")
        print("  2. IAM user has rekognition:DetectLabels and rekognition:DetectFaces permissions")
        print("  3. Region is correct")


if __name__ == "__main__":
    asyncio.run(test_aws_connection())
