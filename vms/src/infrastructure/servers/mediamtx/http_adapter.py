import requests
from typing import Dict, Any, Optional
from .adapter import MediaMTXAdapter

class HTTPMediaMTXAdapter(MediaMTXAdapter):
    
    def __init__(self, base_url: str = "http://mediamtx:9997"):
        self.base_url = base_url
    
    def add_path(self, path_name: str, source_url: str) -> bool:
        try:
            response = requests.post(
                f"{self.base_url}/v3/config/paths/add/{path_name}",
                json={
                    "source": source_url,
                    "sourceOnDemand": False
                },
                timeout=5
            )
            return response.status_code in [200, 201]
        except Exception:
            return False
    
    def remove_path(self, path_name: str) -> bool:
        try:
            response = requests.post(
                f"{self.base_url}/v3/config/paths/remove/{path_name}",
                timeout=5
            )
            return response.status_code in [200, 204]
        except Exception:
            return False
    
    def path_exists(self, path_name: str) -> bool:
        try:
            response = requests.get(
                f"{self.base_url}/v3/paths/list",
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                items = data.get('items', [])
                return any(item['name'] == path_name for item in items)
            return False
        except Exception:
            return False
    
    def get_hls_url(self, path_name: str) -> str:
        return f"/hls/{path_name}/index.m3u8"
    
    def get_all_paths(self) -> Optional[Dict[str, Any]]:
        try:
            response = requests.get(
                f"{self.base_url}/v3/paths/list",
                timeout=5
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception:
            return None
    
    def update_path_config(self, path_name: str, config: Dict[str, Any]) -> bool:
        try:
            response = requests.patch(
                f"{self.base_url}/v3/config/paths/edit/{path_name}",
                json=config,
                timeout=5
            )
            return response.status_code == 200
        except Exception:
            return False
    
    def get_path(self, path_name: str) -> Optional[Dict[str, Any]]:
        try:
            response = requests.get(
                f"{self.base_url}/v3/paths/get/{path_name}",
                timeout=5
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception:
            return None
