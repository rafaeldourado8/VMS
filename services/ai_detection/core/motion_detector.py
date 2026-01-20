import cv2
import numpy as np
import logging

class MotionDetector:
    def __init__(self, threshold=0.03, var_threshold=16, history=500):
        self.threshold = threshold
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
            history=history,
            varThreshold=var_threshold,
            detectShadows=True
        )
        self.kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        self.logger = logging.getLogger(__name__)
    
    def detect(self, frame: np.ndarray) -> tuple[bool, float]:
        fg_mask = self.bg_subtractor.apply(frame)
        
        # Remove ruído
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, self.kernel)
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, self.kernel)
        
        # Calcula ratio de movimento
        motion_pixels = cv2.countNonZero(fg_mask)
        total_pixels = frame.shape[0] * frame.shape[1]
        motion_ratio = motion_pixels / total_pixels
        
        has_motion = motion_ratio > self.threshold
        
        return has_motion, motion_ratio
