import cv2
import numpy as np
import os
import logging
from ultralytics import YOLO
from fast_plate_ocr.inference.plate_recognizer import LicensePlateRecognizer
from typing import List, Tuple, Optional
from datetime import datetime
from config import settings

logger = logging.getLogger(__name__)

class VehicleDetector:
    """
    Detector de veículos e reconhecedor de placas integrado.
    Combina YOLO para detecção de objetos e fast-plate-ocr para LPR.
    """
    
    def __init__(self):
        self._setup_gpu()
        self._setup_directories()
        
        # Carrega YOLO
        os.environ['YOLO_VERBOSE'] = 'False'
        logger.info(f"Loading YOLO model: {settings.yolo_model}")
        self.yolo = YOLO(settings.yolo_model)
        
        # Carrega LPR
        try:
            logger.info(f"Loading LPR model: {settings.ocr_model}")
            self.plate_recognizer = LicensePlateRecognizer(
                hub_ocr_model=settings.ocr_model
            )
            self.lpr_available = True
            logger.info("LPR model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load LPR model: {e}")
            self.plate_recognizer = None
            self.lpr_available = False
        
        logger.info(f"VehicleDetector initialized - LPR: {self.lpr_available}")
    
    def _setup_gpu(self):
        """Configura GPU se disponível."""
        if settings.enable_gpu:
            import torch
            if torch.cuda.is_available():
                logger.info(f"GPU available: {torch.cuda.get_device_name(0)}")
            else:
                logger.warning("GPU enabled in config but CUDA not available")
        else:
            logger.info("Running in CPU mode")
    
    def _setup_directories(self):
        """Cria diretórios necessários."""
        for directory in [settings.captures_dir, settings.pending_training_dir]:
            os.makedirs(directory, exist_ok=True)
        logger.debug(f"Directories ready: {settings.captures_dir}, {settings.pending_training_dir}")
    
    def detect(self, image: np.ndarray, camera_id: int = 0) -> List[dict]:
        """
        Detecta veículos e reconhece placas na imagem.
        
        Args:
            image: Imagem BGR do OpenCV
            camera_id: ID da câmera (para logging e salvamento)
            
        Returns:
            Lista de detecções com formato:
            {
                "object_type": str,
                "confidence": float,
                "bbox": {"x": int, "y": int, "w": int, "h": int},
                "plate_number": str (opcional),
                "plate_confidence": float (opcional),
                "image_path": str (opcional)
            }
        """
        # YOLO detection
        results = self.yolo(
            image, 
            conf=settings.confidence_threshold,
            classes=settings.vehicle_classes,
            verbose=False
        )
        
        detections = []
        plate_crops = []
        plate_metadata = []
        
        for result in results:
            boxes = result.boxes
            for box in boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                cls = int(box.cls[0])
                
                # Crop do veículo
                vehicle_crop = image[y1:y2, x1:x2]
                
                # Detecção base
                detection = {
                    "object_type": self._get_class_name(cls),
                    "confidence": round(conf, 3),
                    "bbox": {"x": x1, "y": y1, "w": x2-x1, "h": y2-y1},
                    "camera_id": camera_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                # Tenta detectar placa dentro do crop do veículo
                if self.lpr_available and vehicle_crop.size > 0:
                    plate_crop = self._extract_plate_region(vehicle_crop)
                    if plate_crop is not None and plate_crop.size > 0:
                        plate_crops.append(plate_crop)
                        plate_metadata.append({
                            "detection": detection,
                            "crop": plate_crop
                        })
                
                detections.append(detection)
        
        # Reconhecimento de placas em batch (mais eficiente)
        if plate_crops and self.lpr_available:
            try:
                recognized_plates = self.plate_recognizer.run(plate_crops)
                
                for i, plate_text in enumerate(recognized_plates):
                    if plate_text and len(plate_text) > 3:  # Filtra resultados muito curtos
                        metadata = plate_metadata[i]
                        detection = metadata["detection"]
                        plate_crop = metadata["crop"]
                        
                        # Adiciona informações da placa
                        detection["plate_number"] = plate_text
                        detection["plate_confidence"] = 0.9  # fast-plate-ocr não retorna confidence
                        
                        # Salva crop da placa
                        image_path = self._save_plate_crop(plate_crop, plate_text, camera_id)
                        if image_path:
                            detection["image_path"] = image_path
                        
                        logger.info(f"Plate detected: {plate_text} from camera {camera_id}")
            
            except Exception as e:
                logger.error(f"Error during plate recognition: {e}")
        
        return detections
    
    def _extract_plate_region(self, vehicle_crop: np.ndarray) -> Optional[np.ndarray]:
        """
        Tenta extrair a região da placa do crop do veículo.
        Usa detecção simples baseada em características.
        """
        try:
            # Normaliza tamanho se muito pequeno
            h, w = vehicle_crop.shape[:2]
            if h < 50 or w < 50:
                return None
            
            # A placa geralmente está na parte inferior do veículo
            # Pega os 40% inferiores
            plate_region = vehicle_crop[int(h * 0.6):, :]
            
            return plate_region if plate_region.size > 0 else vehicle_crop
        
        except Exception as e:
            logger.debug(f"Error extracting plate region: {e}")
            return vehicle_crop
    
    def _get_class_name(self, cls: int) -> str:
        """Mapeia classe COCO para nome legível."""
        names = {
            2: "car",
            3: "motorcycle", 
            5: "bus",
            7: "truck"
        }
        return names.get(cls, "vehicle")
    
    def _save_plate_crop(self, crop: np.ndarray, plate_text: str, camera_id: int) -> Optional[str]:
        """
        Salva o crop da placa detectada.
        
        Returns:
            Caminho do arquivo salvo ou None em caso de erro
        """
        try:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
            filename = f"plate_{camera_id}_{plate_text}_{timestamp}.jpg"
            filepath = os.path.join(settings.captures_dir, filename)
            
            cv2.imwrite(filepath, crop)
            logger.debug(f"Saved plate crop: {filepath}")
            
            return filepath
        
        except Exception as e:
            logger.error(f"Error saving plate crop: {e}")
            return None
    
    def save_for_training(self, frame: np.ndarray, plate_text: str) -> bool:
        """
        Salva frame completo para treinamento futuro.
        
        Args:
            frame: Frame completo da câmera
            plate_text: Texto da placa detectada
            
        Returns:
            True se salvou com sucesso
        """
        try:
            if not plate_text or not plate_text.strip():
                return False
            
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
            image_filename = f"{timestamp}.jpg"
            image_path = os.path.join(settings.pending_training_dir, image_filename)
            
            # Salva imagem
            cv2.imwrite(image_path, frame)
            
            # Salva metadata
            txt_path = os.path.join(settings.pending_training_dir, f"{timestamp}.txt")
            with open(txt_path, "w") as f:
                f.write(f"{image_filename},{plate_text}")
            
            logger.debug(f"Saved training data: {plate_text}")
            return True
        
        except Exception as e:
            logger.error(f"Error saving training data: {e}")
            return False
    
    def get_stats(self) -> dict:
        """Retorna estatísticas do detector."""
        return {
            "yolo_loaded": self.yolo is not None,
            "lpr_available": self.lpr_available,
            "confidence_threshold": settings.confidence_threshold,
            "vehicle_classes": settings.vehicle_classes
        }
