from enum import Enum

class VehicleType(Enum):
    """Value Object para tipo de veículo"""
    
    CAR = "car"
    MOTORCYCLE = "motorcycle"
    TRUCK = "truck"
    BUS = "bus"
    UNKNOWN = "unknown"
    
    def __str__(self) -> str:
        return self.value
