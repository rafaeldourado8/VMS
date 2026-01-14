import re
from dataclasses import dataclass

@dataclass(frozen=True)
class CitySlug:
    value: str
    
    def __post_init__(self):
        if not self.value:
            raise ValueError("Slug cannot be empty")
        
        if not re.match(r'^[a-z0-9_-]+$', self.value):
            raise ValueError("Slug must contain only lowercase letters, numbers, hyphens and underscores")
        
        if len(self.value) > 50:
            raise ValueError("Slug must be 50 characters or less")
    
    def __str__(self) -> str:
        return self.value
