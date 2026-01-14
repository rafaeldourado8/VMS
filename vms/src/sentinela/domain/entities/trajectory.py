from dataclasses import dataclass
from .trajectory_point import TrajectoryPoint

@dataclass
class Trajectory:
    search_id: str
    points: list[TrajectoryPoint]
    
    def get_timeline(self) -> list[TrajectoryPoint]:
        """Retorna pontos ordenados por timestamp"""
        return sorted(self.points, key=lambda x: x.timestamp)
    
    def get_cameras_visited(self) -> list[str]:
        """Retorna lista única de câmeras visitadas"""
        return list(set(p.camera_id for p in self.points))
    
    def get_total_detections(self) -> int:
        return len(self.points)
    
    def get_high_confidence_points(self) -> list[TrajectoryPoint]:
        return [p for p in self.points if p.is_high_confidence()]
