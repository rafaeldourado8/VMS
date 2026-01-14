from dataclasses import dataclass

@dataclass(frozen=True)
class Confidence:
    value: float
    
    def __post_init__(self):
        if not 0.0 <= self.value <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")
    
    def is_high(self) -> bool:
        return self.value >= 0.9
    
    def is_valid(self) -> bool:
        return self.value >= 0.75
    
    def __str__(self) -> str:
        return f"{self.value:.2%}"
