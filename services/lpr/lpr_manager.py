import asyncio
import logging
import json
import threading
import pika
from lpr_stream_preview import LPRStreamService
import uvicorn
from fastapi import FastAPI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LPRManager:
    def __init__(self):
        self.active_streams = {}
        self.connection = None
        self.channel = None
        
    def start_monitoring(self):
        """Start RabbitMQ consumer"""
        def consume():
            try:
                self.connection = pika.BlockingConnection(
                    pika.ConnectionParameters('rabbitmq', 5672, '/',
                        pika.PlainCredentials('gtvision_user', 'your-rabbitmq-password-here'))
                )
                self.channel = self.connection.channel()
                self.channel.queue_declare(queue='lpr_queue', durable=True)
                
                def callback(ch, method, properties, body):
                    try:
                        data = json.loads(body)
                        camera_id = data['camera_id']
                        stream_path = data.get('stream_path', f"cam_{camera_id}")
                        input_stream = f"rtsp://mediamtx:8554/{stream_path}"
                        
                        print(f"[RabbitMQ] Processando câmera {camera_id} - Stream: {input_stream}", flush=True)
                        if camera_id not in self.active_streams:
                            self._start_lpr_sync(camera_id, input_stream)
                        ch.basic_ack(delivery_tag=method.delivery_tag)
                    except Exception as e:
                        print(f"[RabbitMQ] Erro: {e}", flush=True)
                
                self.channel.basic_consume(queue='lpr_queue', on_message_callback=callback)
                print("[RabbitMQ] Aguardando mensagens...", flush=True)
                self.channel.start_consuming()
            except Exception as e:
                print(f"[RabbitMQ] Erro de conexão: {e}", flush=True)
        
        thread = threading.Thread(target=consume, daemon=True)
        thread.start()
        print("[RabbitMQ] Thread iniciada", flush=True)
        
    def _start_lpr_sync(self, camera_id, input_stream):
        output_stream = f"rtsp://mediamtx:8554/cam_{camera_id}_ai"
        service = LPRStreamService(camera_id, input_stream, output_stream)
        service.start()
        self.active_streams[camera_id] = service
        print(f"[LPR] Ativo para câmera {camera_id}", flush=True)

manager = LPRManager()
print("=== INICIANDO MONITORAMENTO RABBITMQ ===", flush=True)
manager.start_monitoring()
print("=== MONITORAMENTO INICIADO ===", flush=True)

app = FastAPI()

@app.get("/health")
async def health():
    return {"status": "ok", "active_streams": len(manager.active_streams)}

@app.get("/streams")
async def list_streams():
    return {"streams": list(manager.active_streams.keys())}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")
