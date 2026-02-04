from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from pathlib import Path
from datetime import datetime
import os

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_recordings(request, camera_id=None):
    """Lista gravações disponíveis"""
    print(f"[DEBUG] list_recordings chamado - camera_id={camera_id}, user={request.user}")
    recordings_path = Path("/recordings")
    
    if not recordings_path.exists():
        print("[DEBUG] Path /recordings não existe")
        return Response({"recordings": []})
    
    recordings = []
    
    # Se camera_id especificado, lista apenas dela
    if camera_id:
        cam_dirs = [recordings_path / f"cam_{camera_id}"]
    else:
        cam_dirs = [d for d in recordings_path.iterdir() if d.is_dir() and d.name.startswith("cam_")]
    
    print(f"[DEBUG] Processando {len(cam_dirs)} diretórios de câmeras")
    
    for cam_dir in cam_dirs:
        if not cam_dir.exists():
            continue
            
        cam_id = int(cam_dir.name.split("_")[1])
        
        for date_dir in sorted(cam_dir.iterdir(), reverse=True):
            if not date_dir.is_dir():
                continue
            
            for video_file in sorted(date_dir.glob("*.mp4"), reverse=True):
                stat = video_file.stat()
                filename = video_file.stem
                parts = filename.split("-")
                
                try:
                    # Formato: HH-MM-SS-microseconds.mp4
                    if len(parts) >= 3:
                        timestamp = datetime.strptime(
                            f"{date_dir.name} {parts[0]}:{parts[1]}:{parts[2]}", 
                            "%Y-%m-%d %H:%M:%S"
                        )
                    else:
                        continue
                    
                    recordings.append({
                        "camera_id": cam_id,
                        "date": date_dir.name,
                        "timestamp": timestamp.isoformat(),
                        "filename": video_file.name,
                        "size_mb": round(stat.st_size / (1024*1024), 2),
                        "path": str(video_file.relative_to(recordings_path)),
                        "playback_url": f"/cameras/recordings/playback/{cam_id}/{date_dir.name}/{video_file.name}"
                    })
                except Exception as e:
                    print(f"Erro ao processar {video_file}: {e}")
    
    print(f"[DEBUG] Retornando {len(recordings)} gravações")
    return Response({
        "count": len(recordings),
        "recordings": recordings[:50]  # Limita a 50 mais recentes
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def playback_recording(request, camera_id, date, filename):
    """Retorna vídeo gravado para playback"""
    from django.http import FileResponse, Http404
    
    video_path = Path(f"/recordings/cam_{camera_id}/{date}/{filename}")
    
    if not video_path.exists():
        raise Http404("Gravação não encontrada")
    
    return FileResponse(
        open(video_path, 'rb'),
        content_type='video/mp4',
        as_attachment=False
    )
