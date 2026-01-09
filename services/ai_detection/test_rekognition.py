import asyncio
from unittest.mock import Mock, patch
from infrastructure.providers.rekognition import RekognitionProvider


async def test_rekognition_mock():
    provider = RekognitionProvider()
    
    # Mock image bytes
    fake_image = b'\xff\xd8\xff\xe0\x00\x10JFIF'
    
    # Mock DetectLabels
    with patch.object(provider.client, 'detect_labels') as mock_labels:
        mock_labels.return_value = {
            'Labels': [
                {'Name': 'Person', 'Confidence': 95.5},
                {'Name': 'Car', 'Confidence': 88.2}
            ]
        }
        
        labels = await provider.detect_labels(fake_image)
        print(f"✅ DetectLabels: {len(labels)} labels found")
        for label in labels:
            print(f"  - {label['name']}: {label['confidence']:.1f}%")
    
    # Mock DetectFaces
    with patch.object(provider.client, 'detect_faces') as mock_faces:
        mock_faces.return_value = {
            'FaceDetails': [
                {
                    'BoundingBox': {'Left': 0.1, 'Top': 0.2, 'Width': 0.3, 'Height': 0.4},
                    'Confidence': 99.8,
                    'Emotions': [{'Type': 'HAPPY', 'Confidence': 85.0}],
                    'AgeRange': {'Low': 25, 'High': 35}
                }
            ]
        }
        
        faces = await provider.detect_faces(fake_image)
        print(f"✅ DetectFaces: {len(faces)} faces found")
        for face in faces:
            print(f"  - Confidence: {face['confidence']:.1f}%")
            print(f"  - Age: {face['age_range']}")


if __name__ == "__main__":
    print("Testing Rekognition Provider with mocks...\n")
    asyncio.run(test_rekognition_mock())
    print("\n✅ All tests passed!")
