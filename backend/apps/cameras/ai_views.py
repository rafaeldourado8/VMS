from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from apps.cameras.models import Camera
import requests
import os

AI_SERVICE_URL = os.getenv('AI_SERVICE_URL', 'http://ai_detection_service:8080')

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_ai_processing(request, camera_id):
    try:
        camera = Camera.objects.get(id=camera_id)
        
        payload = {
            "camera_id": camera.id,
            "rtsp_url": camera.rtsp_url,
            "enabled": True
        }

        # Chamada ao FastAPI
        response = requests.post(
            f"{AI_SERVICE_URL}/cameras/{camera_id}/start",
            json=payload,
            timeout=5
        )
        
        # Repassa a resposta do FastAPI para o Frontend
        return Response(response.json(), status=response.status_code)

    except Camera.DoesNotExist:
        return Response({'error': 'Câmera não encontrada'}, status=status.HTTP_404_NOT_FOUND)
    except requests.exceptions.RequestException as e:
        return Response(
            {'error': 'Falha na comunicação com o serviço de IA', 'details': str(e)}, 
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def stop_ai_processing(request, camera_id):
    try:
        # Chamada ao FastAPI para parar
        response = requests.post(
            f"{AI_SERVICE_URL}/cameras/{camera_id}/stop",
            timeout=5
        )
        return Response(response.json(), status=response.status_code)
        
    except requests.exceptions.RequestException as e:
        return Response({'error': str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_ai_status(request, camera_id):
    try:
        response = requests.get(
            f"{AI_SERVICE_URL}/cameras/{camera_id}/status",
            timeout=3
        )
        return Response(response.json(), status=response.status_code)
    except Exception:
        return Response({'status': 'offline'}, status=status.HTTP_200_OK)