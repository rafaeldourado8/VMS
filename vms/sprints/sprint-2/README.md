# 🎯 Sprint 2: Streaming + Gravação (7 dias)

## 📋 Objetivo

Implementar streaming HLS via MediaMTX e gravação cíclica 24/7 com notificações de expiração.

---

## 🏗️ Arquitetura

```
Câmera → MediaMTX → [HLS Stream] → Frontend
              ↓
        [Recording Service]
              ↓
        Storage Cíclico
        (7/15/30 dias)
```

---

## 📦 Entregáveis

### Dia 1-2: Domain Layer

```python
# domain/entities/stream.py
@dataclass
class Stream:
    id: str
    camera_id: str
    hls_url: str
    status: StreamStatus
    started_at: datetime
    
    def stop(self):
        self.status = StreamStatus.STOPPED
```

```python
# domain/entities/recording.py
@dataclass
class Recording:
    id: str
    camera_id: str
    file_path: str
    started_at: datetime
    ended_at: datetime | None
    size_bytes: int
    
    def should_delete(self, retention_days: int) -> bool:
        age = datetime.now() - self.started_at
        return age.days >= retention_days
```

---

### Dia 3-4: Infrastructure (MediaMTX)

```python
# infrastructure/streaming/mediamtx_provider.py
class MediaMTXProvider:
    def create_stream(self, camera_id: str, rtsp_url: str) -> str:
        path = f"camera_{camera_id}"
        self._client.add_path(path, rtsp_url)
        return f"{self.base_url}/{path}/index.m3u8"
```

```python
# infrastructure/recording/ffmpeg_recorder.py
class FFmpegRecorder:
    def start_recording(self, stream_url: str, output_path: str):
        cmd = [
            'ffmpeg', '-i', stream_url,
            '-c', 'copy', '-f', 'segment',
            '-segment_time', '3600',  # 1h por arquivo
            output_path
        ]
        subprocess.Popen(cmd)
```

---

### Dia 5-6: Application Layer

```python
# application/use_cases/start_stream.py
class StartStreamUseCase:
    def execute(self, camera_id: str) -> str:
        camera = self._camera_repo.find_by_id(camera_id)
        hls_url = self._streaming_provider.create_stream(
            camera.id, camera.rtsp_url
        )
        
        stream = Stream(...)
        self._stream_repo.save(stream)
        
        # Inicia gravação
        self._recording_service.start(camera_id, hls_url)
        
        return hls_url
```

```python
# application/services/recording_cleanup.py
class RecordingCleanupService:
    def cleanup_expired(self):
        for city in self._city_repo.list_all():
            recordings = self._recording_repo.list_by_city(city.id)
            
            for rec in recordings:
                if rec.should_delete(city.retention_days):
                    # Notifica 1 dia antes
                    if rec.expires_in_days() == 1:
                        self._notify_expiration(rec)
                    
                    if rec.expires_in_days() == 0:
                        self._delete_recording(rec)
```

---

### Dia 7: Django Admin + Celery

```python
# infrastructure/django/admin/stream_admin.py
@admin.register(StreamModel)
class StreamAdmin(admin.ModelAdmin):
    list_display = ['camera_name', 'status', 'started_at', 'viewers']
    actions = ['stop_streams']
```

```python
# infrastructure/celery/tasks.py
@celery_app.task
def cleanup_recordings_task():
    service = RecordingCleanupService(...)
    service.cleanup_expired()

# Executa diariamente
celery_app.conf.beat_schedule = {
    'cleanup-recordings': {
        'task': 'cleanup_recordings_task',
        'schedule': crontab(hour=2, minute=0)
    }
}
```

---

## ✅ Checklist

- [ ] Stream entity
- [ ] Recording entity
- [ ] MediaMTXProvider
- [ ] FFmpegRecorder
- [ ] StartStreamUseCase
- [ ] StopStreamUseCase
- [ ] RecordingCleanupService
- [ ] Celery tasks
- [ ] Django Admin
- [ ] Notificações

---

## 🎯 Critérios de Sucesso

1. ✅ 1000 câmeras streamando
2. ✅ Gravação 24/7 ativa
3. ✅ Cleanup automático
4. ✅ Notificações 1 dia antes
