from dataclasses import dataclass
from ..exceptions import InvalidStreamPathException


@dataclass(frozen=True)
class StreamPath:
    """Value Object para path do stream no MediaMTX"""
    
    camera_id: int
    
    def __post_init__(self):
        if self.camera_id <= 0:
            raise InvalidStreamPathException(f"Camera ID deve ser positivo: {self.camera_id}")
    
    def to_string(self) -> str:
        """Retorna o path formatado"""
        return f"cam_{self.camera_id}"
    
    def __str__(self) -> str:
        return self.to_string()
