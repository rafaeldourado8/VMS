# fastapi_services/streaming/app/services/pipeline.py
from typing import List
import numpy as np
import logging

from ..core.interfaces import IFrameProcessor

logger = logging.getLogger(__name__)

class ProcessingPipeline:
    """Pipeline de processamento (Composite Pattern)"""
    
    def __init__(self):
        self._processors: List[IFrameProcessor] = []
    
    def add_processor(self, processor: IFrameProcessor) -> 'ProcessingPipeline':
        """Adiciona processador ao pipeline (Fluent Interface)"""
        self._processors.append(processor)
        return self
    
    def remove_processor(self, processor: IFrameProcessor) -> bool:
        """Remove processador do pipeline"""
        try:
            self._processors.remove(processor)
            return True
        except ValueError:
            return False
    
    def clear(self) -> None:
        """Remove todos os processadores"""
        self._processors.clear()
    
    async def process(self, frame: np.ndarray) -> np.ndarray:
        """Processa frame através de todos os processadores"""
        processed_frame = frame
        
        for processor in self._processors:
            try:
                processed_frame = await processor.process(processed_frame)
            except Exception as e:
                logger.error(f"Erro no processador {processor.__class__.__name__}: {str(e)}")
                # Continua com o frame anterior em caso de erro
        
        return processed_frame
    
    def get_processors(self) -> List[IFrameProcessor]:
        """Retorna lista de processadores"""
        return self._processors.copy()
    
    def __len__(self) -> int:
        return len(self._processors)