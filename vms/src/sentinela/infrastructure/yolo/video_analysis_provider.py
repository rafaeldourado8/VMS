import cv2
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from domain.repositories.video_analysis_provider import IVideoAnalysisProvider
from domain.value_objects.search_criteria import SearchCriteria

class YOLOVideoAnalysisProvider(IVideoAnalysisProvider):
    """
    Provedor de análise de vídeo usando YOLO
    Processa gravações para buscar veículos
    """
    
    def __init__(self):
        # TODO: Carregar modelo YOLO
        # self.model = YOLO('yolov8n.pt')
        pass
    
    def analyze_video(self, video_path: str, criteria: SearchCriteria) -> list[dict]:
        """
        Analisa vídeo frame por frame buscando veículos
        
        Processo:
        1. Extrai frames do vídeo (1 FPS)
        2. YOLO detecta veículos
        3. OCR lê placas (se critério de placa)
        4. Compara com critérios
        5. Retorna matches
        """
        if not Path(video_path).exists():
            return []
        
        results = []
        
        # Abre vídeo
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = 0
        
        # Processa 1 frame por segundo
        frame_interval = int(fps) if fps > 0 else 30
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Processa apenas 1 frame por segundo
            if frame_count % frame_interval != 0:
                frame_count += 1
                continue
            
            # Timestamp do frame
            timestamp = self._get_frame_timestamp(video_path, frame_count, fps)
            
            # Detecta veículos
            detections = self._detect_vehicles(frame, criteria)
            
            for detection in detections:
                results.append({
                    'timestamp': timestamp,
                    'confidence': detection['confidence'],
                    'image_url': self._save_frame(frame, video_path, frame_count),
                    'matched_criteria': detection['matched_criteria']
                })
            
            frame_count += 1
        
        cap.release()
        return results
    
    def _detect_vehicles(self, frame: np.ndarray, criteria: SearchCriteria) -> list[dict]:
        """Detecta veículos no frame"""
        # TODO: Implementar detecção real com YOLO
        # results = self.model.predict(frame, conf=0.75)
        # 
        # detections = []
        # for result in results:
        #     if self._matches_criteria(result, criteria):
        #         detections.append({
        #             'confidence': result.confidence,
        #             'matched_criteria': ['plate', 'color', 'type']
        #         })
        # 
        # return detections
        
        # Mock para testes
        return []
    
    def _matches_criteria(self, detection, criteria: SearchCriteria) -> bool:
        """Verifica se detecção corresponde aos critérios"""
        matched = []
        
        # Verifica placa
        if criteria.has_plate():
            # TODO: OCR na placa
            # if plate_matches(detection, criteria.plate):
            #     matched.append('plate')
            pass
        
        # Verifica cor
        if criteria.has_color():
            # TODO: Detectar cor do veículo
            pass
        
        # Verifica tipo
        if criteria.has_vehicle_type():
            # TODO: Classificar tipo de veículo
            pass
        
        return len(matched) > 0
    
    def _get_frame_timestamp(self, video_path: str, frame_number: int, fps: float) -> datetime:
        """Calcula timestamp do frame baseado no nome do arquivo"""
        # Nome do arquivo: 20240115_143000.mp4
        filename = Path(video_path).stem
        
        try:
            # Parse timestamp do nome do arquivo
            video_start = datetime.strptime(filename, '%Y%m%d_%H%M%S')
            
            # Adiciona offset do frame
            seconds_offset = frame_number / fps if fps > 0 else 0
            return video_start + timedelta(seconds=seconds_offset)
        except:
            return datetime.now()
    
    def _save_frame(self, frame: np.ndarray, video_path: str, frame_number: int) -> str:
        """Salva frame como imagem"""
        output_dir = Path(video_path).parent / 'detections'
        output_dir.mkdir(exist_ok=True)
        
        filename = f"{Path(video_path).stem}_frame_{frame_number}.jpg"
        output_path = output_dir / filename
        
        cv2.imwrite(str(output_path), frame)
        
        return str(output_path)
