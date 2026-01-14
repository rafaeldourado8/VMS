# 🎬 Recording Service - Especificação Técnica

## 📋 Visão Geral

Serviço Python responsável por gravação contínua 24/7 de streams de câmeras com gerenciamento automático de armazenamento por plano.

---

## 🏗️ Arquitetura

```python
RecordingService
├── StreamRecorder      # FFmpeg wrapper
├── StorageManager      # Gerenciamento de espaço
├── CleanupScheduler    # Limpeza automática
└── HealthMonitor       # Monitoramento
```

---

## 🔧 Implementação

### 1. Stream Recorder

```python
class StreamRecorder:
    def __init__(self, camera_id: int, rtsp_url: str):
        self.camera_id = camera_id
        self.rtsp_url = rtsp_url
        self.output_dir = f"/recordings/cam_{camera_id}"
        
    def start_recording(self):
        """Inicia gravação contínua em segmentos de 1h"""
        cmd = [
            'ffmpeg',
            '-i', self.rtsp_url,
            '-c:v', 'copy',  # Sem re-encode
            '-c:a', 'aac',
            '-f', 'segment',
            '-segment_time', '3600',  # 1h
            '-segment_format', 'mp4',
            '-strftime', '1',
            f'{self.output_dir}/%Y-%m-%d/%H-00-00.mp4'
        ]
        subprocess.Popen(cmd)
```

### 2. Storage Manager

```python
class StorageManager:
    PLAN_RETENTION = {
        'basic': 7,
        'pro': 15,
        'premium': 30
    }
    
    def cleanup_old_recordings(self, camera_id: int, plan: str):
        """Remove gravações antigas baseado no plano"""
        retention_days = self.PLAN_RETENTION[plan]
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        # Buscar e deletar arquivos antigos
        for recording in Recording.objects.filter(
            camera_id=camera_id,
            created_at__lt=cutoff_date,
            is_clip=False  # Não deletar clipes
        ):
            os.remove(recording.file_path)
            recording.delete()
```

### 3. Cleanup Scheduler

```python
# Celery task
@celery.task
def cleanup_recordings_task():
    """Roda diariamente às 3h da manhã"""
    for camera in Camera.objects.filter(recording_enabled=True):
        user = camera.owner
        StorageManager().cleanup_old_recordings(
            camera.id, 
            user.plan
        )
```

---

## 📁 Estrutura de Arquivos

```
/recordings/
  /cam_1/
    /2026-01-14/
      00-00-00.mp4  # 00:00 - 01:00
      01-00-00.mp4  # 01:00 - 02:00
      ...
      23-00-00.mp4  # 23:00 - 24:00
    /2026-01-15/
      ...
```

---

## 🔌 API Endpoints

### Start Recording
```http
POST /api/recording/start/
{
  "camera_id": 1
}
```

### Stop Recording
```http
POST /api/recording/stop/
{
  "camera_id": 1
}
```

### Get Status
```http
GET /api/recording/status/{camera_id}/
Response: {
  "is_recording": true,
  "current_file": "/recordings/cam_1/2026-01-14/15-00-00.mp4",
  "disk_usage": "45.2 GB",
  "retention_days": 7
}
```

---

## 📊 Models

```python
class Recording(models.Model):
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    file_path = models.CharField(max_length=500)
    file_size = models.BigIntegerField()  # bytes
    duration = models.IntegerField()  # segundos
    is_clip = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['camera', 'start_time']),
            models.Index(fields=['created_at']),
        ]
```

---

## ⚙️ Configuração

### docker-compose.yml
```yaml
recording:
  build: ./services/recording
  volumes:
    - recordings:/recordings
  environment:
    - POSTGRES_HOST=postgres_db
    - REDIS_URL=redis://redis_cache:6379/5
  depends_on:
    - postgres_db
    - mediamtx
```

### .env
```bash
RECORDING_SEGMENT_DURATION=3600  # 1h
RECORDING_FORMAT=mp4
RECORDING_CODEC=h264
RECORDING_BITRATE=2M
```

---

## 🧪 Testes

```python
def test_recording_starts():
    recorder = StreamRecorder(1, "rtsp://test")
    recorder.start_recording()
    assert recorder.is_recording()

def test_cleanup_respects_plan():
    # Basic: 7 dias
    cleanup_old_recordings(camera_id=1, plan='basic')
    assert Recording.objects.filter(
        camera_id=1,
        created_at__lt=datetime.now() - timedelta(days=7)
    ).count() == 0
```

---

## 📈 Métricas

- **Uptime:** 99.9%
- **Frame Loss:** <0.1%
- **Disk I/O:** <100 MB/s
- **CPU Usage:** <20% per camera

---

## 🚨 Alertas

- Disco >80%: Warning
- Disco >90%: Critical
- Recording stopped: Critical
- Frame loss >1%: Warning
