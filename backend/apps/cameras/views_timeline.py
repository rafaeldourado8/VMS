from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from .services import RecordingService
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

@api_view(['GET'])
def camera_recordings(request, camera_id):
    """Lista gravações de uma câmera"""
    date = request.GET.get('date')
    
    try:
        recordings = RecordingService.get_recordings_for_camera(camera_id, date)
        return Response({
            "camera_id": camera_id,
            "date": date or datetime.now().strftime("%Y-%m-%d"),
            "recordings": recordings,
            "count": len(recordings)
        })
    except Exception as e:
        logger.error(f"Erro ao buscar gravações da câmera {camera_id}: {e}")
        return Response(
            {"error": "Erro interno do servidor"}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def camera_recording_dates(request, camera_id):
    """Lista datas disponíveis para uma câmera"""
    try:
        dates = RecordingService.get_recording_dates(camera_id)
        return Response({
            "camera_id": camera_id,
            "available_dates": dates
        })
    except Exception as e:
        logger.error(f"Erro ao buscar datas da câmera {camera_id}: {e}")
        return Response(
            {"error": "Erro interno do servidor"}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def storage_stats(request):
    """Estatísticas de armazenamento"""
    try:
        stats = RecordingService.get_storage_stats()
        return Response(stats)
    except Exception as e:
        logger.error(f"Erro ao buscar estatísticas: {e}")
        return Response(
            {"error": "Erro interno do servidor"}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def timeline_data(request, camera_id):
    """Dados para timeline de gravações"""
    date = request.GET.get('date', datetime.now().strftime("%Y-%m-%d"))
    
    try:
        recordings = RecordingService.get_recordings_for_camera(camera_id, date)
        
        # Converter para formato de timeline
        timeline_segments = []
        for recording in recordings:
            # Extrair hora do nome do arquivo (formato: HH-MM-SS.mp4)
            filename = recording['filename']
            if filename.endswith('.mp4'):
                time_part = filename[:-4]  # Remove .mp4
                try:
                    hour, minute, second = map(int, time_part.split('-'))
                    start_time = f"{hour:02d}:{minute:02d}:{second:02d}"
                    
                    # Assumir duração de 1 hora por segmento (ajustar conforme necessário)
                    end_hour = (hour + 1) % 24
                    end_time = f"{end_hour:02d}:{minute:02d}:{second:02d}"
                    
                    timeline_segments.append({
                        "start": start_time,
                        "end": end_time,
                        "filename": filename,
                        "size_mb": recording['size_mb']
                    })
                except ValueError:
                    # Nome de arquivo não segue o padrão esperado
                    continue
        
        return Response({
            "camera_id": camera_id,
            "date": date,
            "segments": timeline_segments
        })
    except Exception as e:
        logger.error(f"Erro ao buscar timeline da câmera {camera_id}: {e}")
        return Response(
            {"error": "Erro interno do servidor"}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )