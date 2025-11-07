# fastapi_services/streaming/app/services/connection_manager.py
from fastapi import WebSocket
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, camera_id: str):
        """Conecta um cliente ao stream de uma câmera"""
        await websocket.accept()
        
        if camera_id not in self.active_connections:
            self.active_connections[camera_id] = []
        
        self.active_connections[camera_id].append(websocket)
        logger.info(f"Cliente conectado à câmera {camera_id}. Total: {len(self.active_connections[camera_id])}")
    
    def disconnect(self, websocket: WebSocket, camera_id: str):
        """Desconecta um cliente"""
        if camera_id in self.active_connections:
            if websocket in self.active_connections[camera_id]:
                self.active_connections[camera_id].remove(websocket)
                logger.info(f"Cliente desconectado da câmera {camera_id}")
            
            # Remove a lista se estiver vazia
            if not self.active_connections[camera_id]:
                del self.active_connections[camera_id]
    
    async def broadcast(self, camera_id: str, message: bytes):
        """Envia mensagem para todos os clientes conectados a uma câmera"""
        if camera_id not in self.active_connections:
            return
        
        disconnected = []
        
        for connection in self.active_connections[camera_id]:
            try:
                await connection.send_bytes(message)
            except Exception as e:
                logger.error(f"Erro ao enviar para cliente: {str(e)}")
                disconnected.append(connection)
        
        # Remove conexões mortas
        for conn in disconnected:
            self.disconnect(conn, camera_id)
    
    def get_connection_count(self, camera_id: str) -> int:
        """Retorna número de conexões para uma câmera"""
        return len(self.active_connections.get(camera_id, []))
    
    def get_total_connections(self) -> int:
        """Retorna número total de conexões"""
        return sum(len(conns) for conns in self.active_connections.values())