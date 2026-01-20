import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Track:
    track_id: int
    frames: List[Tuple[np.ndarray, Tuple[int, int, int, int]]] = field(default_factory=list)
    first_seen: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)
    
    def add_frame(self, frame: np.ndarray, bbox: Tuple[int, int, int, int]):
        self.frames.append((frame, bbox))
        self.last_seen = datetime.now()
    
    def is_expired(self, timeout: int = 5) -> bool:
        elapsed = (datetime.now() - self.last_seen).total_seconds()
        return elapsed > timeout

class VehicleTracker:
    def __init__(self, iou_threshold: float = 0.3, timeout: int = 5):
        self.iou_threshold = iou_threshold
        self.timeout = timeout
        self.tracks: Dict[int, Track] = {}
        self.next_id = 1
    
    def update(self, detections: list, frame: np.ndarray) -> List[Track]:
        completed = []
        expired = []
        
        # Remove expirados
        for track_id, track in self.tracks.items():
            if track.is_expired(self.timeout):
                expired.append(track_id)
                completed.append(track)
        
        for track_id in expired:
            del self.tracks[track_id]
        
        # Associa detecções
        for det in detections:
            bbox = det['bbox']
            matched = False
            best_iou = 0
            best_id = None
            
            for track_id, track in self.tracks.items():
                last_bbox = track.frames[-1][1]
                iou = self._iou(bbox, last_bbox)
                
                if iou > self.iou_threshold and iou > best_iou:
                    best_iou = iou
                    best_id = track_id
                    matched = True
            
            if matched and best_id:
                self.tracks[best_id].add_frame(frame, bbox)
            else:
                new_track = Track(track_id=self.next_id)
                new_track.add_frame(frame, bbox)
                self.tracks[self.next_id] = new_track
                self.next_id += 1
        
        return completed
    
    @staticmethod
    def _iou(bbox1: Tuple[int, int, int, int], bbox2: Tuple[int, int, int, int]) -> float:
        x1_1, y1_1, x2_1, y2_1 = bbox1
        x1_2, y1_2, x2_2, y2_2 = bbox2
        
        x1_i = max(x1_1, x1_2)
        y1_i = max(y1_1, y1_2)
        x2_i = min(x2_1, x2_2)
        y2_i = min(y2_1, y2_2)
        
        if x2_i < x1_i or y2_i < y1_i:
            return 0.0
        
        intersection = (x2_i - x1_i) * (y2_i - y1_i)
        area1 = (x2_1 - x1_1) * (y2_1 - y1_1)
        area2 = (x2_2 - x1_2) * (y2_2 - y1_2)
        union = area1 + area2 - intersection
        
        return intersection / union if union > 0 else 0.0
