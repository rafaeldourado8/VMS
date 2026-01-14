import requests
from domain.repositories.streaming_provider import IStreamingProvider

class MediaMTXProvider(IStreamingProvider):
    def __init__(self, base_url: str = "http://mediamtx:9997"):
        self.base_url = base_url
        self.hls_base_url = "http://mediamtx:8888"
    
    def create_stream(self, camera_id: str, stream_url: str) -> str:
        """
        Configura MediaMTX para receber stream da câmera
        MediaMTX automaticamente cria HLS quando recebe RTSP/RTMP
        """
        path = f"camera_{camera_id}"
        
        # MediaMTX API para configurar source
        config = {
            "name": path,
            "source": stream_url,
            "sourceOnDemand": False,  # Sempre ativo
            "runOnReady": "",
            "runOnDemand": ""
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/v3/config/paths/add/{path}",
                json=config,
                timeout=5
            )
            response.raise_for_status()
        except Exception as e:
            # MediaMTX pode já ter o path configurado
            pass
        
        # Retorna URL HLS
        return f"{self.hls_base_url}/{path}/index.m3u8"
    
    def delete_stream(self, camera_id: str) -> None:
        path = f"camera_{camera_id}"
        try:
            requests.delete(
                f"{self.base_url}/v3/config/paths/remove/{path}",
                timeout=5
            )
        except Exception:
            pass
    
    def is_stream_active(self, camera_id: str) -> bool:
        path = f"camera_{camera_id}"
        try:
            response = requests.get(
                f"{self.base_url}/v3/paths/get/{path}",
                timeout=5
            )
            return response.status_code == 200
        except Exception:
            return False
