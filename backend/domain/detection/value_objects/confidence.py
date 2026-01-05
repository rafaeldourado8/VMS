from dataclasses import dataclass
from typing import Optional
from ..exceptions import InvalidConfidenceException


@dataclass(frozen=True)
class Confidence:
    """Value Object para confiança da detecção (0.0 a 1.0)"""
    
    value: Optional[float]
    
    def __post_init__(self):
        if self.value is not None:
            if not 0.0 <= self.value <= 1.0:
                raise InvalidConfidenceException(
                    f"Confiança deve estar entre 0.0 e 1.0: {self.value}"
                )
    
    def is_high(self, threshold: float = 0.8) -> bool:
        """Verifica se a confiança é alta"""
        return self.value is not None and self.value >= threshold
    
    def is_low(self, threshold: float = 0.5) -> bool:
        """Verifica se a confiança é baixa"""
        return self.value is not None and self.value < threshold
    
    def __float__(self) -> float:
        return self.value if self.value is not None else 0.0
