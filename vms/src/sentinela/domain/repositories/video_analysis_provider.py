from abc import ABC, abstractmethod
from domain.value_objects.search_criteria import SearchCriteria

class IVideoAnalysisProvider(ABC):
    """Interface para análise de vídeo (YOLO + Rekognition)"""
    
    @abstractmethod
    def analyze_video(self, video_path: str, criteria: SearchCriteria) -> list[dict]:
        """
        Analisa vídeo buscando veículos que correspondem aos critérios
        
        Returns: [
            {
                'timestamp': datetime,
                'confidence': float,
                'image_url': str,
                'matched_criteria': ['plate', 'color', 'type']
            }
        ]
        """
        pass
