from dataclasses import dataclass

@dataclass(frozen=True)
class SearchCriteria:
    plate: str | None = None
    color: str | None = None
    vehicle_type: str | None = None
    
    def has_plate(self) -> bool:
        return self.plate is not None and len(self.plate) > 0
    
    def has_color(self) -> bool:
        return self.color is not None and len(self.color) > 0
    
    def has_vehicle_type(self) -> bool:
        return self.vehicle_type is not None and len(self.vehicle_type) > 0
    
    def is_empty(self) -> bool:
        return not (self.has_plate() or self.has_color() or self.has_vehicle_type())
