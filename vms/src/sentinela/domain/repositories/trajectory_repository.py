from abc import ABC, abstractmethod
from domain.entities.trajectory import Trajectory

class ITrajectoryRepository(ABC):
    @abstractmethod
    def save(self, trajectory: Trajectory) -> None:
        pass
    
    @abstractmethod
    def find_by_search_id(self, search_id: str) -> Trajectory | None:
        pass
    
    @abstractmethod
    def delete(self, search_id: str) -> None:
        pass
