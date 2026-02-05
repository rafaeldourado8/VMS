from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Recording
from .serializers import RecordingSerializer
import httpx

class RecordingViewSet(viewsets.ModelViewSet):
    queryset = Recording.objects.all()
    serializer_class = RecordingSerializer
    filterset_fields = ['camera_id', 'date', 'is_valid']
    
    @action(detail=False, methods=['get'])
    def by_camera(self, request):
        camera_id = request.query_params.get('camera_id')
        date = request.query_params.get('date')
        
        recordings = Recording.objects.filter(camera_id=camera_id)
        if date:
            recordings = recordings.filter(date=date)
        
        serializer = self.get_serializer(recordings, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    async def sync_from_service(self, request):
        """Sincroniza gravações do Recording Service"""
        camera_id = request.data.get('camera_id')
        date = request.data.get('date')
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"http://recording:8006/recordings/{camera_id}",
                params={"date": date}
            )
            data = response.json()
            
            for file_info in data['files']:
                Recording.objects.update_or_create(
                    camera_id=camera_id,
                    date=date,
                    file_name=file_info['name'],
                    defaults={
                        'file_path': file_info['path'],
                        'size_mb': file_info['size_mb']
                    }
                )
        
        return Response({"status": "synced"})
