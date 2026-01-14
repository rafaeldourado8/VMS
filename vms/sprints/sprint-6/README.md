# 🎯 Sprint 6: YOLO Real + Recording Service (7 dias)

## 📋 Objetivo

Implementar YOLO real com modelo treinado e Recording Service com FFmpeg.

---

## 🚀 Entregáveis

### Dia 1-2: YOLO Real + OCR

#### YOLO Detection Provider
```python
# lpr/infrastructure/yolo/detection_provider.py
from ultralytics import YOLO
from pathlib import Path
import cv2
import numpy as np

class YOLODetectionProvider(IDetectionProvider):
    def __init__(self, model_path: str = None):
        if model_path is None:
            model_path = Path(__file__).parent / 'models' / 'yolov8n.pt'
        
        self.model = YOLO(model_path)
        self.model.to('cpu')  # CPU-only
        
        # Fast-Plate-OCR
        from fast_plate_ocr import ONNXPlateRecognizer
        self.ocr = ONNXPlateRecognizer('brazilian-plates')
    
    def detect_plates(self, frame: np.ndarray) -> list[dict]:
        # 1. YOLO detecta veículos
        results = self.model.predict(
            frame,
            conf=0.75,
            classes=[2, 3, 5, 7],  # car, motorcycle, bus, truck
            verbose=False
        )
        
        detections = []
        for result in results[0].boxes:
            # 2. Extrai região da placa
            x1, y1, x2, y2 = map(int, result.xyxy[0])
            vehicle_img = frame[y1:y2, x1:x2]
            
            # 3. Detecta placa no veículo
            plate_region = self._find_plate_region(vehicle_img)
            if plate_region is None:
                continue
            
            # 4. OCR na placa
            plate_text = self.ocr.run(plate_region)
            if not plate_text:
                continue
            
            # 5. Valida formato brasileiro
            if not self._is_valid_brazilian_plate(plate_text):
                continue
            
            detections.append({
                'plate': plate_text,
                'confidence': float(result.conf[0]),
                'bbox': [x1, y1, x2, y2]
            })
        
        return detections
    
    def _find_plate_region(self, vehicle_img: np.ndarray):
        """Encontra região da placa no veículo"""
        # Converte para cinza
        gray = cv2.cvtColor(vehicle_img, cv2.COLOR_BGR2GRAY)
        
        # Detecta bordas
        edges = cv2.Canny(gray, 100, 200)
        
        # Encontra contornos
        contours, _ = cv2.findContours(
            edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
        )
        
        # Filtra por proporção de placa (3:1)
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = w / h if h > 0 else 0
            
            if 2.5 < aspect_ratio < 4.5:  # Proporção de placa
                return vehicle_img[y:y+h, x:x+w]
        
        return None
    
    def _is_valid_brazilian_plate(self, plate: str) -> bool:
        """Valida formato de placa brasileira"""
        import re
        
        # Formato antigo: ABC1234
        old_format = re.match(r'^[A-Z]{3}\d{4}$', plate)
        
        # Formato Mercosul: ABC1D23
        mercosul_format = re.match(r'^[A-Z]{3}\d[A-Z]\d{2}$', plate)
        
        return bool(old_format or mercosul_format)
```

---

### Dia 3-4: Recording Service com FFmpeg

#### Recording Service
```python
# streaming/infrastructure/recording/ffmpeg_recorder.py
import subprocess
import asyncio
from pathlib import Path

class FFmpegRecorder:
    def __init__(self, storage_path: str = '/recordings'):
        self.storage_path = Path(storage_path)
        self.processes = {}
    
    async def start_recording(
        self,
        camera_id: str,
        stream_url: str,
        retention_days: int
    ) -> str:
        """Inicia gravação 24/7"""
        output_dir = self.storage_path / camera_id
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_pattern = str(output_dir / '%Y%m%d_%H%M%S.mp4')
        
        # FFmpeg command
        cmd = [
            'ffmpeg',
            '-i', stream_url,
            '-c:v', 'copy',  # Copia codec (sem re-encode)
            '-c:a', 'copy',
            '-f', 'segment',
            '-segment_time', '3600',  # 1 hora por arquivo
            '-segment_format', 'mp4',
            '-strftime', '1',
            '-reset_timestamps', '1',
            output_pattern
        ]
        
        # Inicia processo
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        self.processes[camera_id] = process
        
        # Monitora processo
        asyncio.create_task(self._monitor_process(camera_id, process))
        
        return str(output_dir)
    
    async def stop_recording(self, camera_id: str):
        """Para gravação"""
        if camera_id in self.processes:
            process = self.processes[camera_id]
            process.terminate()
            await process.wait()
            del self.processes[camera_id]
    
    async def _monitor_process(self, camera_id: str, process):
        """Monitora processo FFmpeg"""
        while True:
            line = await process.stderr.readline()
            if not line:
                break
            
            # Log de progresso
            print(f"[{camera_id}] {line.decode().strip()}")
```

#### Recording Cleanup Service
```python
# streaming/application/services/recording_cleanup.py
import asyncio
from pathlib import Path
from datetime import datetime, timedelta

class RecordingCleanupService:
    async def cleanup_expired(self, retention_days: int):
        """Remove gravações expiradas"""
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        deleted_count = 0
        for recording in await self._recording_repo.list_all():
            if recording.is_permanent:
                continue
            
            if recording.started_at < cutoff_date:
                # Notifica 1 dia antes
                if recording.expires_in_days(retention_days) == 1:
                    await self._notify_expiration(recording)
                
                # Deleta arquivo
                Path(recording.file_path).unlink(missing_ok=True)
                await self._recording_repo.delete(recording.id)
                deleted_count += 1
        
        return deleted_count
```

---

### Dia 5-6: Celery Tasks

#### Celery Configuration
```python
# config/celery.py
from celery import Celery
from celery.schedules import crontab

app = Celery('vms')
app.config_from_object('config.settings', namespace='CELERY')

# Beat schedule
app.conf.beat_schedule = {
    'cleanup-recordings-daily': {
        'task': 'streaming.tasks.cleanup_recordings',
        'schedule': crontab(hour=2, minute=0),  # 2 AM
    },
    'process-lpr-frames': {
        'task': 'lpr.tasks.process_frames',
        'schedule': 0.33,  # 3 FPS
    },
}
```

#### Tasks
```python
# streaming/tasks.py
from celery import shared_task

@shared_task
def cleanup_recordings():
    """Task para limpeza de gravações"""
    service = RecordingCleanupService(...)
    deleted = await service.cleanup_expired(retention_days=7)
    return f"Deleted {deleted} recordings"

@shared_task
def start_recording_task(camera_id: str, stream_url: str):
    """Inicia gravação assíncrona"""
    recorder = FFmpegRecorder()
    await recorder.start_recording(camera_id, stream_url, retention_days=7)
```

```python
# lpr/tasks.py
from celery import shared_task

@shared_task
def process_frame_task(camera_id: str, frame_bytes: bytes):
    """Processa frame para detecção"""
    frame = cv2.imdecode(
        np.frombuffer(frame_bytes, np.uint8),
        cv2.IMREAD_COLOR
    )
    
    use_case = ProcessFrameUseCase(...)
    detections = use_case.execute(ProcessFrameRequest(
        camera_id=camera_id,
        city_id=city_id,
        frame=frame
    ))
    
    return len(detections)
```

---

### Dia 7: Testes + Otimização

#### Testes de Performance
```python
# tests/performance/test_yolo_performance.py
import pytest
import time

def test_yolo_detection_speed():
    provider = YOLODetectionProvider()
    frame = cv2.imread('test_image.jpg')
    
    start = time.time()
    detections = provider.detect_plates(frame)
    elapsed = time.time() - start
    
    assert elapsed < 0.1  # < 100ms
    assert len(detections) > 0

def test_recording_performance():
    recorder = FFmpegRecorder()
    
    start = time.time()
    await recorder.start_recording('test', 'rtsp://test')
    elapsed = time.time() - start
    
    assert elapsed < 1.0  # < 1s para iniciar
```

---

## ✅ Checklist

### YOLO
- [ ] Carregar modelo treinado
- [ ] Detectar veículos (classes 2,3,5,7)
- [ ] Encontrar região da placa
- [ ] OCR com Fast-Plate-OCR
- [ ] Validar formato brasileiro

### Recording
- [ ] FFmpegRecorder (async)
- [ ] Gravação em segmentos (1h)
- [ ] RecordingCleanupService
- [ ] Notificações de expiração

### Celery
- [ ] Configuração do Celery
- [ ] Task de cleanup (diária)
- [ ] Task de processamento (3 FPS)
- [ ] Monitoring de tasks

### Testes
- [ ] Testes de performance YOLO
- [ ] Testes de recording
- [ ] Testes de cleanup

---

## 🎯 Métricas de Sucesso

1. ✅ YOLO detectando placas reais
2. ✅ OCR com >90% precisão
3. ✅ Recording 24/7 funcionando
4. ✅ Cleanup automático
5. ✅ Processamento < 100ms por frame

---

## 🚀 Próximo Sprint

**Sprint 7:** Sentinela + Deploy
