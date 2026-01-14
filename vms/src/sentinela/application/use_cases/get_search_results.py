from domain.entities.trajectory import Trajectory
from domain.repositories.vehicle_search_repository import IVehicleSearchRepository
from domain.repositories.trajectory_repository import ITrajectoryRepository

class GetSearchResultsUseCase:
    def __init__(
        self,
        search_repo: IVehicleSearchRepository,
        trajectory_repo: ITrajectoryRepository
    ):
        self._search_repo = search_repo
        self._trajectory_repo = trajectory_repo
    
    def execute(self, search_id: str) -> dict:
        search = self._search_repo.find_by_id(search_id)
        if not search:
            raise ValueError(f"Search {search_id} not found")
        
        trajectory = self._trajectory_repo.find_by_search_id(search_id)
        
        return {
            'search': search,
            'trajectory': trajectory,
            'timeline': trajectory.get_timeline() if trajectory else [],
            'cameras_visited': trajectory.get_cameras_visited() if trajectory else [],
            'total_detections': trajectory.get_total_detections() if trajectory else 0
        }
