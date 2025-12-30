#!/usr/bin/env python3
"""
Teste de detecção de IA - Envia frame da câmera para processamento
"""

import json
import pika
import base64
import subprocess
from datetime import datetime

def test_ai_detection():
    print("🧪 Testando detecção de IA...")
    
    # Conecta ao RabbitMQ
    rabbitmq_url = 'amqp://gtvision_user:your-rabbitmq-password-here@rabbitmq_ai:5672/'
    params = pika.URLParameters(rabbitmq_url)
    
    try:
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        print("✅ Conectado ao RabbitMQ")
    except Exception as e:
        print(f"❌ Erro conectando ao RabbitMQ: {e}")
        return
    
    # Captura frame da câmera via FFmpeg
    print("📸 Capturando frame da câmera...")
    
    cmd = [
        'ffmpeg',
        '-i', 'http://mediamtx:8888/camera1/index.m3u8',
        '-vframes', '1',
        '-f', 'image2pipe',
        '-vcodec', 'png',
        '-'
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, timeout=10)
        
        if result.returncode == 0 and result.stdout:
            frame_data = base64.b64encode(result.stdout).decode()
            print(f"✅ Frame capturado ({len(frame_data)} bytes)")
            
            # Envia para processamento
            message = {
                'camera_id': 1,
                'frame_number': 1,
                'timestamp': datetime.now().isoformat(),
                'frame_data': frame_data
            }
            
            channel.basic_publish(
                exchange='',
                routing_key='ai_frames',
                body=json.dumps(message),
                properties=pika.BasicProperties(delivery_mode=2)
            )
            
            print("✅ Frame enviado para processamento de IA")
            
        else:
            print(f"❌ Erro capturando frame: {result.stderr.decode()}")
            
    except subprocess.TimeoutExpired:
        print("❌ Timeout capturando frame")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    finally:
        connection.close()

if __name__ == "__main__":
    test_ai_detection()