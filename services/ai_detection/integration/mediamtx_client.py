import requests
import logging
from typing import Optional, Dict

class MediaMTXClient:
    def __init__(self, base_url: str = "http://mediamtx:9997"):
        self.base_url = base_url.rstrip('/')
        self.api_url = f"{self.base_url}/v3"
        self.logger = logging.getLogger(__name__)
    
    def get_path_info(self, path_name: str) -> Optional[Dict]:
        """Obtém informações de um path do MediaMTX"""
        try:
            response = requests.get(
                f"{self.api_url}/paths/get/{path_name}",
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.warning(f"Path {path_name} not found: {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to get path info for {path_name}: {e}")
            return None
    
    def list_paths(self) -> list:
        """Lista todos os paths ativos no MediaMTX"""
        try:
            response = requests.get(f"{self.api_url}/paths/list", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('items', [])
            else:
                self.logger.error(f"Failed to list paths: {response.status_code}")
                return []
                
        except Exception as e:
            self.logger.error(f"Failed to list paths: {e}")
            return []
    
    def get_rtsp_url(self, camera_id: int) -> str:
        """Gera URL RTSP para uma câmera (fallback se WebRTC falhar)"""
        host = self.base_url.split('//')[1].split(':')[0]
        return f"rtsp://{host}:8554/cam_{camera_id}"
    
    def get_webrtc_url(self, camera_id: int) -> str:
        """Gera URL WebRTC para uma câmera"""
        # MediaMTX WebRTC usa HTTP/HTTPS para signaling
        return f"{self.base_url.replace('9997', '8889')}/cam_{camera_id}/whep"
