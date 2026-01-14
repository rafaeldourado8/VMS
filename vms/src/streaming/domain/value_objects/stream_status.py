from enum import Enum

class StreamStatus(Enum):
    ACTIVE = 'active'
    STOPPED = 'stopped'
    ERROR = 'error'
    
    @property
    def display_name(self) -> str:
        return {
            StreamStatus.ACTIVE: 'Active',
            StreamStatus.STOPPED: 'Stopped',
            StreamStatus.ERROR: 'Error'
        }[self]
