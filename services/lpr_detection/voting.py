"""
Plate Voting System
Sistema de consenso para determinar a placa correta baseado em múltiplas leituras
"""

from typing import List, Dict, Tuple, Optional
from collections import Counter
import difflib


class PlateVoter:
    """
    Sistema de votação para determinar placa correta
    Usa múltiplas estratégias de consenso
    """
    
    def __init__(self, min_detections: int = 3):
        """
        Args:
            min_detections: Mínimo de detecções para considerar confiável
        """
        self.min_detections = min_detections
    
    def vote(self, 
             plates: List[str], 
             confidences: List[float]) -> Optional[Tuple[str, float, str]]:
        """
        Determina placa correta por votação
        
        Args:
            plates: Lista de placas detectadas
            confidences: Lista de confianças correspondentes
        
        Returns:
            (placa_final, confiança_final, método_usado) ou None
        """
        if not plates or len(plates) != len(confidences):
            return None
        
        # Estratégia 1: Maioria simples (se houver consenso claro)
        result = self._simple_majority(plates, confidences)
        if result:
            return result
        
        # Estratégia 2: Similaridade (placas parecidas)
        result = self._similarity_voting(plates, confidences)
        if result:
            return result
        
        # Estratégia 3: Maior confiança
        result = self._highest_confidence(plates, confidences)
        return result
    
    def _simple_majority(self, 
                        plates: List[str], 
                        confidences: List[float]) -> Optional[Tuple[str, float, str]]:
        """
        Votação por maioria simples
        Se uma placa aparece >50% das vezes, ela vence
        """
        if len(plates) < self.min_detections:
            return None
        
        counter = Counter(plates)
        most_common = counter.most_common(1)[0]
        plate, count = most_common
        
        # Precisa de maioria (>50%)
        if count > len(plates) / 2:
            # Confiança média das detecções dessa placa
            plate_confidences = [
                conf for p, conf in zip(plates, confidences) if p == plate
            ]
            avg_confidence = sum(plate_confidences) / len(plate_confidences)
            
            return plate, avg_confidence, "simple_majority"
        
        return None
    
    def _similarity_voting(self, 
                          plates: List[str], 
                          confidences: List[str]) -> Optional[Tuple[str, float, str]]:
        """
        Votação por similaridade
        Agrupa placas similares (ex: ABC1234 e ABC1Z34)
        """
        if len(plates) < self.min_detections:
            return None
        
        # Agrupa placas similares (>80% de similaridade)
        groups: Dict[str, List[Tuple[str, float]]] = {}
        
        for plate, conf in zip(plates, confidences):
            matched = False
            
            for group_key in groups.keys():
                similarity = difflib.SequenceMatcher(None, plate, group_key).ratio()
                if similarity > 0.8:  # 80% similar
                    groups[group_key].append((plate, conf))
                    matched = True
                    break
            
            if not matched:
                groups[plate] = [(plate, conf)]
        
        # Encontra maior grupo
        largest_group = max(groups.items(), key=lambda x: len(x[1]))
        group_key, group_items = largest_group
        
        if len(group_items) > len(plates) / 2:
            # Escolhe placa com maior confiança do grupo
            best_plate, best_conf = max(group_items, key=lambda x: x[1])
            avg_conf = sum(c for _, c in group_items) / len(group_items)
            
            return best_plate, avg_conf, "similarity_voting"
        
        return None
    
    def _highest_confidence(self, 
                           plates: List[str], 
                           confidences: List[float]) -> Tuple[str, float, str]:
        """
        Fallback: Retorna placa com maior confiança
        """
        max_idx = confidences.index(max(confidences))
        return plates[max_idx], confidences[max_idx], "highest_confidence"
    
    def get_confidence_level(self, confidence: float, method: str) -> str:
        """
        Classifica nível de confiança
        
        Returns:
            'high', 'medium', 'low'
        """
        if method == "simple_majority" and confidence >= 0.85:
            return "high"
        elif method == "similarity_voting" and confidence >= 0.80:
            return "medium"
        elif confidence >= 0.90:
            return "high"
        elif confidence >= 0.75:
            return "medium"
        else:
            return "low"


# Exemplo de uso
if __name__ == "__main__":
    voter = PlateVoter(min_detections=3)
    
    # Cenário 1: Consenso claro
    print("=== Cenário 1: Consenso Claro ===")
    plates1 = ["ABC1234", "ABC1234", "ABC1234", "ABC1Z34", "ABC1234"]
    confs1 = [0.85, 0.90, 0.88, 0.75, 0.92]
    
    result = voter.vote(plates1, confs1)
    if result:
        plate, conf, method = result
        level = voter.get_confidence_level(conf, method)
        print(f"Placa: {plate}")
        print(f"Confiança: {conf:.2f}")
        print(f"Método: {method}")
        print(f"Nível: {level}")
    
    print("\n=== Cenário 2: Placas Similares ===")
    plates2 = ["ABC1234", "ABC1Z34", "ABC1234", "ABC1234", "ABC1Z34"]
    confs2 = [0.85, 0.80, 0.90, 0.88, 0.82]
    
    result = voter.vote(plates2, confs2)
    if result:
        plate, conf, method = result
        level = voter.get_confidence_level(conf, method)
        print(f"Placa: {plate}")
        print(f"Confiança: {conf:.2f}")
        print(f"Método: {method}")
        print(f"Nível: {level}")
    
    print("\n=== Cenário 3: Sem Consenso ===")
    plates3 = ["ABC1234", "XYZ5678", "DEF9012"]
    confs3 = [0.85, 0.90, 0.88]
    
    result = voter.vote(plates3, confs3)
    if result:
        plate, conf, method = result
        level = voter.get_confidence_level(conf, method)
        print(f"Placa: {plate}")
        print(f"Confiança: {conf:.2f}")
        print(f"Método: {method}")
        print(f"Nível: {level}")
