"""
Vehicle Tracking System
Rastreia veículos entre frames para acumular leituras de placa
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta


@dataclass
class Detection:
    """Detecção única de veículo/placa"""
    bbox: Tuple[int, int, int, int]  # x1, y1, x2, y2
    plate_text: str
    confidence: float
    frame_id: int
    timestamp: datetime


@dataclass
class Vehicle:
    """Veículo rastreado ao longo de múltiplos frames"""
    track_id: int
    detections: List[Detection] = field(default_factory=list)
    first_seen: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)
    
    def add_detection(self, detection: Detection):
        """Adiciona nova detecção ao veículo"""
        self.detections.append(detection)
        self.last_seen = detection.timestamp
    
    def get_best_plate(self) -> Optional[Tuple[str, float]]:
        """Retorna placa com maior consenso (voting)"""
        if not self.detections:
            return None
        
        # Agrupa por placa e conta ocorrências
        plate_votes: Dict[str, List[float]] = {}
        for det in self.detections:
            if det.plate_text not in plate_votes:
                plate_votes[det.plate_text] = []
            plate_votes[det.plate_text].append(det.confidence)
        
        # Calcula score: (quantidade × confiança média)
        best_plate = None
        best_score = 0
        
        for plate, confidences in plate_votes.items():
            count = len(confidences)
            avg_confidence = np.mean(confidences)
            score = count * avg_confidence
            
            if score > best_score:
                best_score = score
                best_plate = plate
        
        if best_plate:
            avg_conf = np.mean(plate_votes[best_plate])
            return best_plate, avg_conf
        
        return None
    
    def is_expired(self, timeout_seconds: int = 5) -> bool:
        """Verifica se veículo saiu do campo de visão"""
        elapsed = (datetime.now() - self.last_seen).total_seconds()
        return elapsed > timeout_seconds


class VehicleTracker:
    """
    Rastreia veículos entre frames usando IoU (Intersection over Union)
    """
    
    def __init__(self, iou_threshold: float = 0.3, timeout_seconds: int = 5):
        self.iou_threshold = iou_threshold
        self.timeout_seconds = timeout_seconds
        self.vehicles: Dict[int, Vehicle] = {}
        self.next_track_id = 1
    
    def update(self, detections: List[Detection]) -> List[Vehicle]:
        """
        Atualiza tracker com novas detecções
        
        Returns:
            Lista de veículos que saíram do campo de visão (completos)
        """
        # Remove veículos expirados
        completed_vehicles = []
        expired_ids = []
        
        for track_id, vehicle in self.vehicles.items():
            if vehicle.is_expired(self.timeout_seconds):
                expired_ids.append(track_id)
                completed_vehicles.append(vehicle)
        
        for track_id in expired_ids:
            del self.vehicles[track_id]
        
        # Associa novas detecções a veículos existentes
        for detection in detections:
            matched = False
            best_iou = 0
            best_track_id = None
            
            # Encontra melhor match por IoU
            for track_id, vehicle in self.vehicles.items():
                last_det = vehicle.detections[-1]
                iou = self._calculate_iou(detection.bbox, last_det.bbox)
                
                if iou > self.iou_threshold and iou > best_iou:
                    best_iou = iou
                    best_track_id = track_id
                    matched = True
            
            if matched and best_track_id:
                # Adiciona a veículo existente
                self.vehicles[best_track_id].add_detection(detection)
            else:
                # Cria novo veículo
                new_vehicle = Vehicle(track_id=self.next_track_id)
                new_vehicle.add_detection(detection)
                self.vehicles[self.next_track_id] = new_vehicle
                self.next_track_id += 1
        
        return completed_vehicles
    
    @staticmethod
    def _calculate_iou(bbox1: Tuple[int, int, int, int], 
                       bbox2: Tuple[int, int, int, int]) -> float:
        """
        Calcula Intersection over Union entre duas bounding boxes
        
        Args:
            bbox1, bbox2: (x1, y1, x2, y2)
        
        Returns:
            IoU score (0.0 - 1.0)
        """
        x1_1, y1_1, x2_1, y2_1 = bbox1
        x1_2, y1_2, x2_2, y2_2 = bbox2
        
        # Área de interseção
        x1_i = max(x1_1, x1_2)
        y1_i = max(y1_1, y1_2)
        x2_i = min(x2_1, x2_2)
        y2_i = min(y2_1, y2_2)
        
        if x2_i < x1_i or y2_i < y1_i:
            return 0.0
        
        intersection = (x2_i - x1_i) * (y2_i - y1_i)
        
        # Área de união
        area1 = (x2_1 - x1_1) * (y2_1 - y1_1)
        area2 = (x2_2 - x1_2) * (y2_2 - y1_2)
        union = area1 + area2 - intersection
        
        return intersection / union if union > 0 else 0.0
    
    def get_active_vehicles(self) -> List[Vehicle]:
        """Retorna veículos atualmente sendo rastreados"""
        return list(self.vehicles.values())


# Exemplo de uso
if __name__ == "__main__":
    tracker = VehicleTracker(iou_threshold=0.3, timeout_seconds=5)
    
    # Simular detecções em múltiplos frames
    frame_detections = [
        # Frame 1
        [
            Detection(bbox=(100, 100, 200, 200), plate_text="ABC1234", confidence=0.85, frame_id=1, timestamp=datetime.now()),
        ],
        # Frame 2 (mesmo carro, posição ligeiramente diferente)
        [
            Detection(bbox=(110, 105, 210, 205), plate_text="ABC1234", confidence=0.90, frame_id=2, timestamp=datetime.now()),
        ],
        # Frame 3 (OCR errou)
        [
            Detection(bbox=(120, 110, 220, 210), plate_text="ABC1Z34", confidence=0.75, frame_id=3, timestamp=datetime.now()),
        ],
        # Frame 4 (correto novamente)
        [
            Detection(bbox=(130, 115, 230, 215), plate_text="ABC1234", confidence=0.92, frame_id=4, timestamp=datetime.now()),
        ],
    ]
    
    for frame_dets in frame_detections:
        completed = tracker.update(frame_dets)
        
        for vehicle in completed:
            best_plate = vehicle.get_best_plate()
            if best_plate:
                plate, confidence = best_plate
                print(f"Veículo {vehicle.track_id}: {plate} (confiança: {confidence:.2f})")
                print(f"  Total de detecções: {len(vehicle.detections)}")
