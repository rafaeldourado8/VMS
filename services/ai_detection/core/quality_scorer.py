import cv2
import numpy as np
from typing import Tuple

class QualityScorer:
    def __init__(self, blur_w=0.35, angle_w=0.30, contrast_w=0.20, size_w=0.15):
        self.weights = {
            'blur': blur_w,
            'angle': angle_w,
            'contrast': contrast_w,
            'size': size_w
        }
    
    def score(self, frame: np.ndarray, bbox: Tuple[int, int, int, int]) -> dict:
        blur = self._blur_score(frame)
        angle = self._angle_score(bbox, frame.shape[1])
        contrast = self._contrast_score(frame)
        size = self._size_score(bbox)
        
        final = (
            blur * self.weights['blur'] +
            angle * self.weights['angle'] +
            contrast * self.weights['contrast'] +
            size * self.weights['size']
        )
        
        return {
            'final': final,
            'blur': blur,
            'angle': angle,
            'contrast': contrast,
            'size': size
        }
    
    def _blur_score(self, frame: np.ndarray) -> float:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        variance = laplacian.var()
        return min(100, (variance / 500) * 100)
    
    def _angle_score(self, bbox: Tuple[int, int, int, int], frame_width: int) -> float:
        x1, _, x2, _ = bbox
        center_x = (x1 + x2) / 2
        frame_center = frame_width / 2
        offset = abs(center_x - frame_center) / frame_center
        return (1 - offset) * 100
    
    def _contrast_score(self, frame: np.ndarray) -> float:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        std = np.std(hist)
        return min(100, (std / 50) * 100)
    
    def _size_score(self, bbox: Tuple[int, int, int, int]) -> float:
        x1, y1, x2, y2 = bbox
        area = (x2 - x1) * (y2 - y1)
        
        if area < 2000:
            return (area / 2000) * 50
        elif area > 50000:
            return 50
        else:
            return 50 + ((area - 2000) / (50000 - 2000)) * 50
