from dataclasses import dataclass


@dataclass(frozen=True)
class HLSUrl:
    """Value Object para URL HLS do stream"""
    
    base_url: str
    path: str
    
    def to_string(self) -> str:
        """Retorna a URL HLS completa"""
        return f"{self.base_url}/{self.path}/index.m3u8"
    
    def __str__(self) -> str:
        return self.to_string()
