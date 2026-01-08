from .metric import Metric
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class Dashboard:
    """Entidade de domínio para dashboard"""
    
    metrics: List[Metric]
    summary: Dict[str, Any]
    
    def get_metric_by_name(self, name: str) -> Metric:
        """Busca métrica por nome"""
        for metric in self.metrics:
            if metric.name == name:
                return metric
        raise ValueError(f"Métrica '{name}' não encontrada")
    
    def total_detections(self) -> int:
        """Total de detecções"""
        try:
            metric = self.get_metric_by_name("total_detections")
            return int(metric.value)
        except ValueError:
            return 0
    
    def active_cameras(self) -> int:
        """Câmeras ativas"""
        try:
            metric = self.get_metric_by_name("active_cameras")
            return int(metric.value)
        except ValueError:
            return 0