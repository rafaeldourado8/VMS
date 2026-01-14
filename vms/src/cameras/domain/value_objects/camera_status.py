from enum import Enum

class CameraStatus(Enum):
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    ERROR = 'error'
    
    @property
    def display_name(self) -> str:
        return {
            CameraStatus.ACTIVE: 'Active',
            CameraStatus.INACTIVE: 'Inactive',
            CameraStatus.ERROR: 'Error'
        }[self]
