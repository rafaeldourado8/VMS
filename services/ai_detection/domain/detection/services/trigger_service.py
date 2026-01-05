from typing import Dict, Optional
from ..entities.vehicle import Vehicle
from ..entities.virtual_line import VirtualLine
from ..value_objects.point import Point


class TriggerService:
    """Serviço de domínio para lógica de trigger P1-P2"""
    
    def __init__(self, p1_line: VirtualLine, p2_line: VirtualLine):
        self.p1_line = p1_line
        self.p2_line = p2_line
        self.vehicles: Dict[int, Vehicle] = {}
    
    def update_vehicle(self, vehicle: Vehicle) -> None:
        """Atualiza veículo e verifica cruzamento de linhas"""
        track_id = vehicle.track_id
        
        if track_id not in self.vehicles:
            self.vehicles[track_id] = vehicle
            return
        
        prev_vehicle = self.vehicles[track_id]
        prev_pos = prev_vehicle.bbox.center()
        curr_pos = vehicle.bbox.center()
        
        # Verifica cruzamento P1
        if not prev_vehicle.crossed_p1 and self.p1_line.intersects(prev_pos, curr_pos):
            vehicle.mark_crossed_p1()
        
        # Verifica cruzamento P2
        if prev_vehicle.crossed_p1 and not prev_vehicle.crossed_p2:
            if self.p2_line.intersects(prev_pos, curr_pos):
                vehicle.mark_crossed_p2()
        
        # Atualiza registro
        self.vehicles[track_id] = vehicle
    
    def should_activate_ocr(self, track_id: int) -> bool:
        """Verifica se deve ativar OCR para este veículo"""
        if track_id not in self.vehicles:
            return False
        return self.vehicles[track_id].is_ready_for_trigger()
    
    def calculate_velocity(self, track_id: int, distance_meters: float, fps: float = 1.0) -> Optional[float]:
        """Calcula velocidade do veículo entre P1 e P2"""
        if track_id not in self.vehicles:
            return None
        
        vehicle = self.vehicles[track_id]
        if not (vehicle.crossed_p1 and vehicle.crossed_p2):
            return None
        
        if len(vehicle.positions) < 2:
            return None
        
        # Tempo em segundos (baseado no número de frames)
        time_seconds = len(vehicle.positions) / fps
        
        if time_seconds == 0:
            return None
        
        # Velocidade em m/s
        velocity_ms = distance_meters / time_seconds
        
        # Converte para km/h
        velocity_kmh = velocity_ms * 3.6
        
        return velocity_kmh
    
    def cleanup_vehicle(self, track_id: int) -> None:
        """Remove veículo do tracking"""
        if track_id in self.vehicles:
            del self.vehicles[track_id]
