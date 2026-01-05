from ..commands.update_roi_command import UpdateROICommand
from domain.detection.entities.roi import ROI
from domain.detection.value_objects.polygon import Polygon
from domain.detection.value_objects.point import Point


class UpdateROIHandler:
    """Handler para atualizar ROI"""
    
    def __init__(self, config_repository):
        self.config_repository = config_repository
    
    def handle(self, command: UpdateROICommand) -> ROI:
        """Atualiza ROI de uma câmera"""
        
        # Converte pontos para value objects
        points = tuple(Point(x=p[0], y=p[1]) for p in command.polygon_points)
        polygon = Polygon(points=points)
        
        # Cria ROI
        roi = ROI(
            camera_id=command.camera_id,
            polygon=polygon,
            enabled=command.enabled,
            name=command.name
        )
        
        # Salva configuração
        config = self.config_repository.get_or_create(command.camera_id)
        config['roi'] = {
            'points': command.polygon_points,
            'enabled': command.enabled,
            'name': command.name
        }
        self.config_repository.save(command.camera_id, config)
        
        return roi
