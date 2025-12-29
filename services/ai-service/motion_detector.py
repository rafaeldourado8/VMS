import cv2
import numpy as np
import logging
from typing import Tuple, Optional
from config import settings

logger = logging.getLogger(__name__)

class MotionDetector:
    """
    Detector de movimento usando Background Subtraction.
    Otimiza o uso de recursos ao processar apenas frames com movimento significativo.
    """
    
    def __init__(self, 
                 history: int = 500,
                 var_threshold: int = 16,
                 detect_shadows: bool = False):
        """
        Inicializa o detector de movimento.
        
        Args:
            history: Número de frames para construir o modelo de background
            var_threshold: Limiar para detecção de foreground
            detect_shadows: Se deve detectar sombras (mais CPU-intensivo)
        """
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
            history=history,
            varThreshold=var_threshold,
            detectShadows=detect_shadows
        )
        self.min_contour_area = settings.motion_threshold
        self.min_change_percentage = settings.motion_min_change
        self.frame_count = 0
        self.motion_detected_count = 0
        
        logger.info(f"MotionDetector initialized: threshold={self.min_contour_area}, "
                   f"min_change={self.min_change_percentage}")
    
    def detect(self, frame: np.ndarray) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Detecta movimento no frame.
        
        Args:
            frame: Frame BGR do OpenCV
            
        Returns:
            Tuple contendo:
                - bool: True se movimento significativo foi detectado
                - np.ndarray: Máscara de movimento (opcional, para debug)
        """
        self.frame_count += 1
        
        # Aplica o background subtractor
        fg_mask = self.bg_subtractor.apply(frame)
        
        # Remove ruído
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)
        
        # Calcula a porcentagem de mudança
        total_pixels = fg_mask.shape[0] * fg_mask.shape[1]
        changed_pixels = cv2.countNonZero(fg_mask)
        change_percentage = changed_pixels / total_pixels
        
        # Encontra contornos
        contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Verifica se há movimento significativo
        motion_detected = False
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > self.min_contour_area:
                motion_detected = True
                break
        
        # Também considera a porcentagem total de mudança
        if change_percentage > self.min_change_percentage:
            motion_detected = True
        
        if motion_detected:
            self.motion_detected_count += 1
        
        # Log estatísticas periodicamente
        if self.frame_count % 100 == 0:
            motion_rate = (self.motion_detected_count / self.frame_count) * 100
            logger.debug(f"Motion stats - Frames: {self.frame_count}, "
                        f"Motion detected: {self.motion_detected_count} ({motion_rate:.1f}%)")
        
        return motion_detected, fg_mask
    
    def reset(self):
        """Reseta o modelo de background. Útil quando a câmera muda drasticamente."""
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2()
        self.frame_count = 0
        self.motion_detected_count = 0
        logger.info("MotionDetector reset")
    
    def get_stats(self) -> dict:
        """Retorna estatísticas do detector."""
        motion_rate = (self.motion_detected_count / self.frame_count * 100) if self.frame_count > 0 else 0
        return {
            "frames_processed": self.frame_count,
            "motion_detected_count": self.motion_detected_count,
            "motion_rate_percentage": round(motion_rate, 2)
        }
