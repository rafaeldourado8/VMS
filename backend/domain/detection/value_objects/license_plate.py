from ..exceptions import InvalidLicensePlateException
from dataclasses import dataclass
from typing import Optional
import re

@dataclass(frozen=True)
class LicensePlate:
    """Value Object para placa de veículo"""
    
    value: Optional[str]
    
    def __post_init__(self):
        if self.value:
            normalized = self._normalize(self.value)
            object.__setattr__(self, 'value', normalized)
            
            if not self._is_valid_format(normalized):
                raise InvalidLicensePlateException(
                    f"Formato de placa inválido: {self.value}"
                )
    
    @staticmethod
    def _normalize(plate: str) -> str:
        """Remove espaços e caracteres especiais, converte para maiúsculas"""
        return re.sub(r'[^A-Z0-9]', '', plate.upper())
    
    @staticmethod
    def _is_valid_format(plate: str) -> bool:
        """Valida formato brasileiro (ABC1234 ou ABC1D23)"""
        if len(plate) != 7:
            return False
        return bool(re.match(r'^[A-Z]{3}[0-9][A-Z0-9][0-9]{2}$', plate))
    
    def __str__(self) -> str:
        return self.value or ""
