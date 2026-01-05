from dataclasses import dataclass
from typing import Final
from ..exceptions import InvalidStreamUrlException


@dataclass(frozen=True)
class StreamUrl:
    """Value Object para URL de stream RTSP"""
    
    value: str
    
    def __post_init__(self):
        if not self.value:
            raise InvalidStreamUrlException("URL não pode ser vazia")
        
        if not self.value.startswith(("rtsp://", "http://", "https://")):
            raise InvalidStreamUrlException(
                f"URL deve começar com rtsp://, http:// ou https://: {self.value}"
            )
    
    def __str__(self) -> str:
        return self.value
