from typing import Optional
from collections import Counter
import difflib

class ConsensusEngine:
    def __init__(self, min_readings=3, consensus_threshold=0.6, similarity_threshold=0.8):
        self.min_readings = min_readings
        self.consensus_threshold = consensus_threshold
        self.similarity_threshold = similarity_threshold
    
    def vote(self, readings: list) -> Optional[dict]:
        if not readings or len(readings) < self.min_readings:
            return None
        
        plates = [r['plate'] for r in readings]
        confidences = [r['confidence'] for r in readings]
        
        # Estratégia 1: Maioria simples
        result = self._simple_majority(plates, confidences)
        if result:
            return result
        
        # Estratégia 2: Similaridade
        result = self._similarity_voting(plates, confidences)
        if result:
            return result
        
        # Estratégia 3: Maior confiança
        return self._highest_confidence(plates, confidences)
    
    def _simple_majority(self, plates: list, confidences: list) -> Optional[dict]:
        counter = Counter(plates)
        most_common = counter.most_common(1)[0]
        plate, count = most_common
        
        if count > len(plates) / 2:
            plate_confs = [c for p, c in zip(plates, confidences) if p == plate]
            avg_conf = sum(plate_confs) / len(plate_confs)
            
            return {
                'plate': plate,
                'confidence': avg_conf,
                'method': 'simple_majority',
                'votes': count,
                'total': len(plates)
            }
        return None
    
    def _similarity_voting(self, plates: list, confidences: list) -> Optional[dict]:
        groups = {}
        
        for plate, conf in zip(plates, confidences):
            matched = False
            
            for group_key in groups.keys():
                similarity = difflib.SequenceMatcher(None, plate, group_key).ratio()
                if similarity > self.similarity_threshold:
                    groups[group_key].append((plate, conf))
                    matched = True
                    break
            
            if not matched:
                groups[plate] = [(plate, conf)]
        
        largest_group = max(groups.items(), key=lambda x: len(x[1]))
        group_key, group_items = largest_group
        
        if len(group_items) > len(plates) / 2:
            best_plate, best_conf = max(group_items, key=lambda x: x[1])
            avg_conf = sum(c for _, c in group_items) / len(group_items)
            
            return {
                'plate': best_plate,
                'confidence': avg_conf,
                'method': 'similarity_voting',
                'votes': len(group_items),
                'total': len(plates)
            }
        return None
    
    def _highest_confidence(self, plates: list, confidences: list) -> dict:
        max_idx = confidences.index(max(confidences))
        return {
            'plate': plates[max_idx],
            'confidence': confidences[max_idx],
            'method': 'highest_confidence',
            'votes': 1,
            'total': len(plates)
        }
