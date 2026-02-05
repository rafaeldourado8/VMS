import os
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from django.http import HttpResponse, FileResponse, Http404
from django.views.decorators.http import require_http_methods
from apps.cameras.models import Camera
from apps.cameras.models_recording import Recording

RECORDINGS_PATH = Path("/recordings")
HLS_CACHE_PATH = Path("/tmp/hls_playback")
HLS_CACHE_PATH.mkdir(exist_ok=True)

@require_http_methods(["GET"])
def playback_hls_manifest(request, camera_id, date, time):
    """
    Serve HLS manifest for playback.
    URL: /playback/camera/{camera_id}/{YYYY-MM-DD}/{HH-MM}.m3u8
    """
    try:
        # Parse timestamp
        dt = datetime.strptime(f"{date} {time.replace('-', ':')}", "%Y-%m-%d %H:%M")
        
        # Find recording that contains this timestamp
        recording = Recording.objects.filter(
            camera_id=camera_id,
            started_at__lte=dt,
            ended_at__gte=dt
        ).first()
        
        if not recording:
            return HttpResponse("No recording found for this time", status=404)
        
        video_path = RECORDINGS_PATH / recording.video_path.lstrip('/')
        if not video_path.exists():
            return HttpResponse("Recording file not found", status=404)
        
        # Calculate offset from recording start
        offset_seconds = int((dt - recording.started_at).total_seconds())
        
        # Generate HLS on-demand
        cache_key = f"cam{camera_id}_{date}_{time}"
        manifest_path = HLS_CACHE_PATH / f"{cache_key}.m3u8"
        
        # Generate if not cached or old
        if not manifest_path.exists() or (datetime.now().timestamp() - manifest_path.stat().st_mtime) > 300:
            cmd = [
                "ffmpeg", "-y",
                "-ss", str(offset_seconds),
                "-i", str(video_path),
                "-t", "300",  # 5 minutes
                "-c", "copy",
                "-f", "hls",
                "-hls_time", "2",
                "-hls_list_size", "0",
                "-hls_segment_filename", str(HLS_CACHE_PATH / f"{cache_key}_%03d.ts"),
                str(manifest_path)
            ]
            
            subprocess.run(cmd, capture_output=True, timeout=30)
        
        if not manifest_path.exists():
            return HttpResponse("Failed to generate HLS", status=500)
        
        with open(manifest_path, 'r') as f:
            content = f.read()
        
        return HttpResponse(content, content_type='application/vnd.apple.mpegurl')
    
    except Exception as e:
        return HttpResponse(f"Error: {str(e)}", status=500)


@require_http_methods(["GET"])
def playback_hls_segment(request, camera_id, date, time, segment):
    """
    Serve HLS segment.
    URL: /playback/camera/{camera_id}/{YYYY-MM-DD}/{HH-MM}_{segment}.ts
    """
    cache_key = f"cam{camera_id}_{date}_{time}"
    segment_path = HLS_CACHE_PATH / f"{cache_key}_{segment}"
    
    if not segment_path.exists():
        raise Http404("Segment not found")
    
    return FileResponse(open(segment_path, 'rb'), content_type='video/mp2t')


@require_http_methods(["GET"])
def list_recordings_for_date(request, camera_id, date):
    """
    List available recordings for a specific date.
    URL: /api/cameras/{camera_id}/recordings/{YYYY-MM-DD}
    """
    from django.http import JsonResponse
    
    try:
        dt = datetime.strptime(date, "%Y-%m-%d")
        next_day = dt + timedelta(days=1)
        
        recordings = Recording.objects.filter(
            camera_id=camera_id,
            started_at__gte=dt,
            started_at__lt=next_day
        ).order_by('started_at')
        
        data = [{
            'start': rec.started_at.isoformat(),
            'end': rec.ended_at.isoformat() if rec.ended_at else None,
            'type': 'continuous',
            'duration': rec.duration_seconds,
            'file_size': rec.file_size_bytes
        } for rec in recordings]
        
        return JsonResponse(data, safe=False)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
