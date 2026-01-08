from .services import ThumbnailService

from django.http import HttpResponse
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

class CameraSnapshotView(APIView):
    """Retorna uma imagem JPEG do stream atual."""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, camera_id=None):
        service = ThumbnailService()
        image_data = service.get_snapshot(camera_id)

        if image_data:
            return HttpResponse(image_data, content_type="image/jpeg")
        
        return Response(
            {"error": "Snapshot indisponível. Câmara offline ou timeout."}, 
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )