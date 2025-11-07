from typing import List, Dict, Optional
from datetime import datetime, timedelta
import logging
import uuid

from ..schemas import DetectionResult, AlertConfig, AlertResponse, Detection

logger = logging.getLogger(__name__)

class AlertService:
    def __init__(self):
        self.alert_history: Dict[str, datetime] = {}  # camera_id -> last_alert_time
        self.alert_configs: Dict[str, AlertConfig] = {}
    
    def check_alerts(
        self, 
        result: DetectionResult, 
        config: AlertConfig
    ) -> List[AlertResponse]:
        """Verifica se deve gerar alertas baseado nas detecções"""
        alerts = []
        
        if not config.enabled:
            return alerts
        
        camera_id = result.camera_id
        
        # Verifica cooldown
        if self._is_in_cooldown(camera_id, config.cooldown):
            return alerts
        
        # Filtra detecções por confiança
        high_conf_detections = [
            d for d in result.detections 
            if d.confidence >= config.min_confidence
        ]
        
        if not high_conf_detections:
            return alerts
        
        # Filtra por classes se especificado
        if config.classes:
            filtered_detections = [
                d for d in high_conf_detections 
                if d.class_name in config.classes
            ]
        else:
            filtered_detections = high_conf_detections
        
        if not filtered_detections:
            return alerts
        
        # Verifica número máximo de objetos
        if config.max_objects and len(filtered_detections) > config.max_objects:
            alert = self._create_alert(
                camera_id=camera_id,
                alert_type="max_objects_exceeded",
                severity="high",
                message=f"Número máximo de objetos excedido: {len(filtered_detections)} > {config.max_objects}",
                detections=filtered_detections
            )
            alerts.append(alert)
        
        # Alerta para classes específicas
        if config.classes:
            for detection in filtered_detections:
                alert = self._create_alert(
                    camera_id=camera_id,
                    alert_type="object_detected",
                    severity=self._get_severity_for_class(detection.class_name),
                    message=f"{detection.class_name.capitalize()} detectado com {detection.confidence:.2%} de confiança",
                    detections=[detection]
                )
                alerts.append(alert)
        
        # Atualiza histórico
        if alerts:
            self.alert_history[camera_id] = datetime.now()
        
        return alerts
    
    def _is_in_cooldown(self, camera_id: str, cooldown: int) -> bool:
        """Verifica se está em período de cooldown"""
        if camera_id not in self.alert_history:
            return False
        
        last_alert = self.alert_history[camera_id]
        time_since_last = (datetime.now() - last_alert).total_seconds()
        
        return time_since_last < cooldown
    
    def _create_alert(
        self,
        camera_id: str,
        alert_type: str,
        severity: str,
        message: str,
        detections: List[Detection]
    ) -> AlertResponse:
        """Cria um alerta"""
        return AlertResponse(
            alert_id=str(uuid.uuid4()),
            camera_id=camera_id,
            alert_type=alert_type,
            severity=severity,
            message=message,
            timestamp=datetime.now(),
            detections=detections
        )
    
    def _get_severity_for_class(self, class_name: str) -> str:
        """Retorna severidade baseada na classe"""
        high_severity = ['person', 'car', 'truck', 'fire']
        medium_severity = ['dog', 'cat', 'bicycle', 'motorcycle']
        
        if class_name in high_severity:
            return "high"
        elif class_name in medium_severity:
            return "medium"
        else:
            return "low"
    
    def set_config(self, camera_id: str, config: AlertConfig):
        """Define configuração de alertas para uma câmera"""
        self.alert_configs[camera_id] = config
    
    def get_config(self, camera_id: str) -> Optional[AlertConfig]:
        """Obtém configuração de alertas de uma câmera"""
        return self.alert_configs.get(camera_id)