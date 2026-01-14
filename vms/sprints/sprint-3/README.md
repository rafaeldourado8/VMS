# 🎯 Sprint 3: LPR Detection (7 dias)

## 📋 Objetivo

Detecção de placas em tempo real usando YOLO + OCR em até 20 câmeras RTSP por cidade.

---

## 🏗️ Arquitetura

```
Câmera RTSP → Frame Extraction → YOLO → OCR → Backend
                                              ↓
                                         PostgreSQL
                                              ↓
                                         WebSocket
                                              ↓
                                         Frontend
```

---

## 📦 Entregáveis

### Dia 1-2: Domain Layer

```python
# domain/entities/detection.py
@dataclass
class Detection:
    id: str
    camera_id: str
    plate: str
    confidence: float
    bbox: BoundingBox
    image_url: str
    detected_at: datetime
    
    def is_high_confidence(self) -> bool:
        return self.confidence >= 0.9
```

```python
# domain/entities/blacklist.py
@dataclass
class BlacklistEntry:
    id: str
    plate: str
    reason: str
    city_id: str
    created_at: datetime
    
    def matches(self, plate: str) -> bool:
        return self.plate.upper() == plate.upper()
```

---

### Dia 3-4: Infrastructure (YOLO + OCR)

```python
# infrastructure/ai/yolo_detector.py
class YOLODetector:
    def __init__(self):
        self.model = YOLO('yolov8n.pt')
    
    def detect_vehicles(self, frame: np.ndarray) -> list[BoundingBox]:
        results = self.model.predict(frame, conf=0.75)
        return [self._to_bbox(r) for r in results]
```

```python
# infrastructure/ai/ocr_engine.py
class OCREngine:
    def read_plate(self, plate_img: np.ndarray) -> str:
        # Fast-Plate-OCR
        result = self.ocr.read(plate_img)
        return self._normalize_plate(result)
```

```python
# infrastructure/ai/detection_provider.py
class DetectionProvider:
    def __init__(self, yolo: YOLODetector, ocr: OCREngine):
        self._yolo = yolo
        self._ocr = ocr
    
    def detect(self, frame: np.ndarray, camera: Camera) -> list[Detection]:
        bboxes = self._yolo.detect_vehicles(frame)
        
        detections = []
        for bbox in bboxes:
            plate_img = self._crop(frame, bbox)
            plate = self._ocr.read_plate(plate_img)
            
            detection = Detection(
                id=uuid4(),
                camera_id=camera.id,
                plate=plate,
                confidence=bbox.confidence,
                bbox=bbox,
                detected_at=datetime.now()
            )
            detections.append(detection)
        
        return detections
```

---

### Dia 5-6: Application Layer

```python
# application/use_cases/process_frame.py
class ProcessFrameUseCase:
    def execute(self, camera_id: str, frame: bytes):
        camera = self._camera_repo.find_by_id(camera_id)
        
        if not camera.is_lpr_enabled():
            return
        
        detections = self._detection_provider.detect(frame, camera)
        
        for detection in detections:
            self._detection_repo.save(detection)
            
            # Verifica blacklist
            if self._is_blacklisted(detection.plate, camera.city_id):
                self._send_alert(detection)
            
            # WebSocket notification
            self._notify_detection(detection)
```

```python
# application/services/detection_pipeline.py
class DetectionPipeline:
    def start(self, camera_id: str):
        while True:
            frame = self._extract_frame(camera_id)
            process_frame_task.delay(camera_id, frame)
            time.sleep(0.33)  # 3 FPS
```

---

### Dia 7: Django Admin + WebSocket

```python
# infrastructure/django/admin/detection_admin.py
@admin.register(DetectionModel)
class DetectionAdmin(admin.ModelAdmin):
    list_display = ['plate', 'camera', 'confidence', 'detected_at']
    list_filter = ['confidence', 'detected_at']
    search_fields = ['plate']
```

```python
# infrastructure/websocket/detection_consumer.py
class DetectionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        camera_id = self.scope['url_route']['kwargs']['camera_id']
        await self.channel_layer.group_add(
            f"camera_{camera_id}",
            self.channel_name
        )
        await self.accept()
    
    async def detection_created(self, event):
        await self.send(text_data=json.dumps(event['detection']))
```

---

## ✅ Checklist

- [ ] Detection entity
- [ ] BlacklistEntry entity
- [ ] YOLODetector
- [ ] OCREngine
- [ ] DetectionProvider
- [ ] ProcessFrameUseCase
- [ ] DetectionPipeline
- [ ] Celery tasks
- [ ] WebSocket consumer
- [ ] Django Admin

---

## 🎯 Critérios de Sucesso

1. ✅ 20 câmeras com LPR
2. ✅ 100+ detecções/hora
3. ✅ WebSocket real-time
4. ✅ Blacklist funcionando
