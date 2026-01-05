from typing import List, Optional
from ..commands.process_frame_command import ProcessFrameCommand
from domain.detection.entities.vehicle import Vehicle
from domain.detection.entities.roi import ROI
from domain.detection.services.trigger_service import TriggerService


class ProcessFrameHandler:
    """Handler para processar frame de vídeo"""
    
    def __init__(
        self,
        yolo_detector,
        ocr_engine,
        trigger_service: TriggerService,
        roi: Optional[ROI] = None
    ):
        self.yolo_detector = yolo_detector
        self.ocr_engine = ocr_engine
        self.trigger_service = trigger_service
        self.roi = roi
    
    def handle(self, command: ProcessFrameCommand) -> List[Vehicle]:
        """Executa detecção de veículos e OCR se necessário"""
        
        # Detecta veículos com YOLO
        detections = self.yolo_detector.detect(command.frame_data)
        
        vehicles = []
        for det in detections:
            vehicle = Vehicle(
                track_id=det['track_id'],
                bbox=det['bbox'],
                confidence=det['confidence'],
                vehicle_type=det['class']
            )
            
            # Filtra por ROI se configurado
            if self.roi and not self.roi.contains_point(vehicle.bbox.center()):
                continue
            
            # Atualiza trigger service
            self.trigger_service.update_vehicle(vehicle)
            
            # Ativa OCR se cruzou P1
            if command.enable_ocr and self.trigger_service.should_activate_ocr(vehicle.track_id):
                plate_result = self.ocr_engine.detect_plate(command.frame_data, vehicle.bbox)
                if plate_result:
                    vehicle.set_plate(plate_result['plate'], plate_result['confidence'])
            
            vehicles.append(vehicle)
        
        return vehicles
