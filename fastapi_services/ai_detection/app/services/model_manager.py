from ultralytics import YOLO
import torch
from typing import Optional, List, Dict
import logging
from pathlib import Path
import os # <-- Adicionado

from ..schemas import ModelInfo
from ..config import settings # <-- Adicionado

logger = logging.getLogger(__name__)

class ModelManager:
    def __init__(self, models_dir: str = "models"):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(exist_ok=True)
        
        self.model: Optional[YOLO] = None
        self.current_model_name: Optional[str] = None
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        # Modelos disponíveis (mantidos para o endpoint /models)
        self.available_models = {
            "yolov8n": "yolov8n.pt",
            "yolov8s": "yolov8s.pt",
            "yolov8m": "yolov8m.pt",
            "yolov8l": "yolov8l.pt",
            "yolov8x": "yolov8x.pt",
        }
        
        logger.info(f"ModelManager inicializado. Dispositivo: {self.device}")
    
    async def load_model(self, model_name: str) -> bool:
        """Carrega um modelo específico (pré-definido)"""
        try:
            if model_name not in self.available_models:
                logger.error(f"Modelo não encontrado: {model_name}")
                return False
            
            model_path = self.available_models[model_name]
            
            logger.info(f"Carregando modelo {model_name}...")
            self.model = YOLO(model_path)
            self.model.to(self.device)
            self.current_model_name = model_name
            
            logger.info(f"Modelo {model_name} carregado com sucesso no {self.device}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao carregar modelo: {str(e)}")
            return False
    
    # --- MUDANÇA AQUI ---
    async def load_default_model(self) -> bool:
        """Carrega o modelo LPR padrão definido no config.py"""
        # Esta função agora carrega o seu modelo customizado por defeito
        model_file = settings.DEFAULT_MODEL
        model_path = os.path.join(self.models_dir, model_file)
        
        logger.info(f"Carregando modelo LPR padrão de: {model_path}")
        return await self.load_custom_model(model_path)
    # ---------------------

    async def load_custom_model(self, model_path: str) -> bool:
        """Carrega um modelo customizado (o seu .pt)"""
        try:
            if not os.path.exists(model_path):
                 logger.error(f"Ficheiro do modelo customizado não encontrado: {model_path}")
                 return False
                 
            logger.info(f"Carregando modelo customizado: {model_path}")
            self.model = YOLO(model_path)
            self.model.to(self.device)
            self.current_model_name = Path(model_path).stem
            
            logger.info(f"Modelo customizado carregado com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao carregar modelo customizado: {str(e)}")
            return False
    
    def list_available_models(self) -> List[ModelInfo]:
        """Lista modelos disponíveis"""
        models = []
        
        for name, path in self.available_models.items():
            models.append(ModelInfo(
                name=name,
                version="8.0",
                type="yolov8",
                classes=self._get_model_classes(name),
                input_size=[640, 640],
                device=self.device,
                loaded=(name == self.current_model_name)
            ))
        
        return models
    
    def get_current_model_info(self) -> Optional[ModelInfo]:
        """Obtém informações do modelo atual"""
        if not self.model or not self.current_model_name:
            return None
        
        return ModelInfo(
            name=self.current_model_name,
            version="custom", # Atualizado
            type="lpr_custom", # Atualizado
            classes=list(self.model.names.values()),
            input_size=[640, 640], # Ajuste se o seu modelo for diferente
            device=self.device,
            loaded=True
        )
    
    def _get_model_classes(self, model_name: str) -> List[str]:
        """Retorna classes do modelo COCO (agora menos relevante)"""
        # Isto é apenas para os modelos genéricos listados
        return [
            'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck',
            'boat', 'traffic light', 'fire hydrant', 'stop sign', 'parking meter', 'bench',
            'bird', 'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra',
            'giraffe', 'backpack', 'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee',
            'skis', 'snowboard', 'sports ball', 'kite', 'baseball bat', 'baseball glove',
            'skateboard', 'surfboard', 'tennis racket', 'bottle', 'wine glass', 'cup',
            'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple', 'sandwich', 'orange',
            'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch',
            'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop', 'mouse',
            'remote', 'keyboard', 'cell phone', 'microwave', 'oven', 'toaster', 'sink',
            'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear', 'hair drier',
            'toothbrush'
        ]