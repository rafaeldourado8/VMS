from domain.entities.vehicle_search import VehicleSearch
from domain.entities.trajectory import Trajectory
from domain.entities.trajectory_point import TrajectoryPoint
from domain.value_objects.search_criteria import SearchCriteria
from domain.repositories.vehicle_search_repository import IVehicleSearchRepository
from domain.repositories.trajectory_repository import ITrajectoryRepository
from domain.repositories.video_analysis_provider import IVideoAnalysisProvider

class SentinelaService:
    """
    Serviço principal do Sentinela
    Processa buscas de veículos em gravações
    """
    
    def __init__(
        self,
        search_repo: IVehicleSearchRepository,
        trajectory_repo: ITrajectoryRepository,
        video_provider: IVideoAnalysisProvider,
        recording_repo  # IRecordingRepository from streaming module
    ):
        self._search_repo = search_repo
        self._trajectory_repo = trajectory_repo
        self._video_provider = video_provider
        self._recording_repo = recording_repo
    
    def process_search(self, search_id: str):
        """Processa busca de veículo"""
        search = self._search_repo.find_by_id(search_id)
        if not search:
            raise ValueError(f"Search {search_id} not found")
        
        try:
            # Marca como processando
            search.start_processing()
            self._search_repo.save(search)
            
            # Cria critérios de busca
            criteria = SearchCriteria(
                plate=search.plate,
                color=search.color,
                vehicle_type=search.vehicle_type
            )
            
            # Lista gravações no período
            recordings = self._recording_repo.list_by_date_range(
                search.city_id,
                search.start_date,
                search.end_date
            )
            
            trajectory_points = []
            
            # Processa cada gravação
            for recording in recordings:
                results = self._video_provider.analyze_video(
                    video_path=recording.file_path,
                    criteria=criteria
                )
                
                for result in results:
                    point = TrajectoryPoint(
                        camera_id=recording.camera_id,
                        camera_name=self._get_camera_name(recording.camera_id),
                        timestamp=result['timestamp'],
                        image_url=result['image_url'],
                        confidence=result['confidence']
                    )
                    trajectory_points.append(point)
            
            # Salva trajetória
            trajectory = Trajectory(
                search_id=search.id,
                points=trajectory_points
            )
            self._trajectory_repo.save(trajectory)
            
            # Marca como completo
            search.complete()
            self._search_repo.save(search)
            
        except Exception as e:
            search.fail(str(e))
            self._search_repo.save(search)
            raise
    
    def _get_camera_name(self, camera_id: str) -> str:
        # TODO: Buscar nome da câmera do repositório
        return f"Camera {camera_id}"
