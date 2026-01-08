# Detection Provider Interface

## Contract
```python
from typing import Protocol
from dataclasses import dataclass

@dataclass
class BoundingBox:
    x: float
    y: float
    width: float
    height: float
    label: str
    confidence: float

@dataclass
class DetectionResult:
    provider: str
    timestamp: datetime
    boxes: list[BoundingBox]
    metadata: dict

class DetectionProvider(Protocol):
    async def detect(
        self,
        frame: bytes,
        config: dict
    ) -> DetectionResult: ...
    
    def get_capabilities(self) -> list[str]: ...
    def get_cost_per_call(self) -> float: ...
```

## Adding New Provider
1. Implement `DetectionProvider` protocol
2. Register in `providers/__init__.py`
3. Add configuration in `config/providers.yaml`
4. No changes to consumer or API code required
