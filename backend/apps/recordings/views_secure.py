from django.http import FileResponse, Http404
from django.contrib.auth.decorators import login_required
import os

@login_required
def serve_recording(request, filename):
    """Serve recording files securely"""
    file_path = os.path.join('/app/recordings', filename)
    
    if not os.path.exists(file_path):
        raise Http404("Recording not found")
    
    return FileResponse(open(file_path, 'rb'), content_type='video/mp4')
