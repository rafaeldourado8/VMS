import os
from pydantic import BaseModel
from typing import Optional, List # <-- Importar List

class Settings(BaseModel):
    app_name: str = "AI Detection Service"
    redis_host: str = os.getenv("REDIS_HOST", "localhost")
    redis_port: int = int(os.getenv("REDIS_PORT", 6379))
    
    # URL para o Django (legado, pode ser usado para outras coisas)
    django_api_url: str = os.getenv("DJANGO_API_URL", "http://localhost:8000")
    ingest_api_key: str = os.getenv("INGEST_API_KEY", "default_key")

    # --- CORREÇÕES AQUI ---
    # Caminho base para os modelos
    MODELS_DIR: str = "models"
    # Modelo padrão a ser carregado no início
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "yolov8n.pt")
    
    # Configuração de CORS usada no main.py
    CORS_ORIGINS: List[str] = ["*"] # Ajuste conforme necessário
    # -----------------------

    # Esta linha existia, mas o main.py usa DEFAULT_MODEL
    # Mantida para evitar quebrar outras partes, caso exista
    model_path: str = os.getenv("MODEL_PATH", "models/yolov8n.pt")


class RabbitMQSettings(BaseModel):
    """Configurações para o publicador RabbitMQ"""
    host: str = os.getenv("RABBITMQ_HOST", "localhost")
    user: str = os.getenv("RABBITMQ_USER", "guest")
    password: str = os.getenv("RABBITMQ_PASS", "guest")
    queue: str = os.getenv("RABBITMQ_QUEUE", "detection_ingest")

    def get_amqp_url(self):
        return f"amqp://{self.user}:{self.password}@{self.host}:5672/"

settings = Settings()
rabbitmq_settings = RabbitMQSettings()