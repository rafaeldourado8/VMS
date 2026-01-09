import boto3
import asyncio
import os
from typing import Dict, Any, List
from botocore.config import Config
from botocore.exceptions import ClientError
import logging

logger = logging.getLogger(__name__)


class RekognitionProvider:
    def __init__(self, region_name: str = None):
        region = region_name or os.getenv('AWS_REGION', 'us-east-1')
        config = Config(
            connect_timeout=5,
            read_timeout=5,
            retries={'max_attempts': 3, 'mode': 'standard'}
        )
        self.client = boto3.client('rekognition', region_name=region, config=config)
    
    async def detect_labels(self, image_bytes: bytes) -> List[Dict[str, Any]]:
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.detect_labels(
                    Image={'Bytes': image_bytes},
                    MaxLabels=10,
                    MinConfidence=70
                )
            )
            
            return [
                {
                    'name': label['Name'],
                    'confidence': label['Confidence'],
                    'type': 'label'
                }
                for label in response.get('Labels', [])
            ]
        except ClientError as e:
            logger.error(f"Rekognition DetectLabels error: {e}")
            return []
    
    async def detect_faces(self, image_bytes: bytes) -> List[Dict[str, Any]]:
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.detect_faces(
                    Image={'Bytes': image_bytes},
                    Attributes=['ALL']
                )
            )
            
            return [
                {
                    'bounding_box': face['BoundingBox'],
                    'confidence': face['Confidence'],
                    'emotions': face.get('Emotions', []),
                    'age_range': face.get('AgeRange', {}),
                    'type': 'face'
                }
                for face in response.get('FaceDetails', [])
            ]
        except ClientError as e:
            logger.error(f"Rekognition DetectFaces error: {e}")
            return []
