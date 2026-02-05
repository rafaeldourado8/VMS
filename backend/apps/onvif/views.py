import httpx
from django.http import HttpResponse, StreamingHttpResponse
from django.views.decorators.http import require_http_methods
from apps.cameras.models import Camera

ONVIF_SERVICE_URL = "http://onvif:8005"

@require_http_methods(["GET"])
def list_recordings(request, camera_id, date):
    """Proxy para serviço ONVIF - lista gravações."""
    try:
        camera = Camera.objects.get(id=camera_id)
        
        with httpx.Client(timeout=30.0) as client:
            resp = client.get(f"{ONVIF_SERVICE_URL}/cameras/{camera_id}/recordings/{date}")
            
            return HttpResponse(
                resp.content,
                status=resp.status_code,
                content_type='application/json'
            )
    
    except Camera.DoesNotExist:
        return HttpResponse('{"error": "Camera not found"}', status=404, content_type='application/json')
    except Exception as e:
        return HttpResponse(f'{{"error": "{str(e)}"}}', status=500, content_type='application/json')

@require_http_methods(["GET"])
def playback_manifest(request, camera_id, date, time):
    """Proxy para serviço ONVIF - manifest HLS."""
    try:
        with httpx.Client(timeout=30.0) as client:
            resp = client.get(f"{ONVIF_SERVICE_URL}/playback/{camera_id}/{date}/{time}.m3u8")
            
            return HttpResponse(
                resp.content,
                status=resp.status_code,
                content_type='application/vnd.apple.mpegurl'
            )
    
    except Exception as e:
        return HttpResponse(f"Error: {str(e)}", status=500)

@require_http_methods(["GET"])
def playback_segment(request, camera_id, date, time, segment):
    """Proxy para serviço ONVIF - segmento HLS."""
    try:
        with httpx.Client(timeout=30.0) as client:
            resp = client.get(f"{ONVIF_SERVICE_URL}/playback/{camera_id}/{date}/{time}_{segment}")
            
            return HttpResponse(
                resp.content,
                status=resp.status_code,
                content_type='video/mp2t'
            )
    
    except Exception as e:
        return HttpResponse(f"Error: {str(e)}", status=500)
