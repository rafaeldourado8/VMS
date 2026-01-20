import json
import logging
from typing import Set
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)

class DetectionWebSocketManager:
    def __init__(self):
        self.active_connections: Set = set()
        
    def connect(self, channel_name: str):
        self.active_connections.add(channel_name)
        logger.info(f"WebSocket connected. Total: {len(self.active_connections)}")
    
    def disconnect(self, channel_name: str):
        self.active_connections.discard(channel_name)
        logger.info(f"WebSocket disconnected. Total: {len(self.active_connections)}")
    
    def get_connections(self):
        return list(self.active_connections)

manager = DetectionWebSocketManager()
