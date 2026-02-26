from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.http import HttpResponse
from .services import ThumbnailService

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

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def clear_thumbnail_cache(request, camera_id=None):
    """Limpa o cache de thumbnails."""
    if camera_id:
        ThumbnailService.clear_cache(camera_id)
        return Response({"success": True, "message": f"Cache da câmera {camera_id} limpo"})
    else:
        from django.core.cache import cache
        cache.clear()
        return Response({"success": True, "message": "Todo cache limpo"})