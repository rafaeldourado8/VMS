# 🤖 LPR Detection - Sistema de Detecção de Placas

## Visão Geral

Sistema de reconhecimento de placas veiculares usando YOLO para detecção e OCR para leitura.

## Stack Tecnológica

### YOLO (You Only Look Once)
- **Modelo:** YOLOv8n (nano)
- **Framework:** Ultralytics
- **Função:** Detectar veículos e placas
- **Performance:** ~30-60 FPS (CPU)

### OCR (Optical Character Recognition)
- **Biblioteca:** Fast-Plate-OCR
- **Função:** Ler caracteres da placa
- **Precisão:** ~95% em condições ideais

### PyTorch
- **Versão:** CPU-only
- **Função:** Backend de inferência
- **Otimização:** Quantização INT8

## Arquitetura

```
RTSP Stream → Frame Extraction → YOLO Detection → OCR → Database
                                        ↓
                                   Crop Plate
```

## Fluxo de Detecção

### 1. Captura de Frames
```python
# A cada N frames (skip frames para performance)
FRAME_SKIP = 3  # Processa 1 a cada 3 frames

cap = cv2.VideoCapture(rtsp_url)
frame_count = 0

while True:
    ret, frame = cap.read()
    if frame_count % FRAME_SKIP == 0:
        process_frame(frame)
    frame_count += 1
```

### 2. Detecção YOLO
```python
# Detecta veículos e placas
results = model.predict(frame, conf=0.5)

for detection in results:
    if detection.class == 'license_plate':
        x1, y1, x2, y2 = detection.bbox
        plate_crop = frame[y1:y2, x1:x2]
        ocr_result = ocr.read(plate_crop)
```

### 3. OCR e Validação
```python
# Lê caracteres da placa
plate_text = ocr.read_plate(plate_crop)

# Valida formato brasileiro
if validate_brazilian_plate(plate_text):
    save_detection(plate_text, frame, timestamp)
```

## Configuração por Câmera

### Modelo de Dados
```python
class Camera(models.Model):
    ai_enabled = models.BooleanField(default=False)
    detection_settings = models.JSONField(default=dict)
    roi_areas = models.JSONField(default=list)
```

### Exemplo de Settings
```json
{
  "confidence_threshold": 0.5,
  "frame_skip": 3,
  "roi_enabled": true,
  "roi_coordinates": [[100, 100], [500, 400]],
  "detection_types": ["vehicle", "license_plate"]
}
```

## ROI (Region of Interest)

### Definição
Área específica do frame onde a detecção é aplicada.

### Benefícios
- **Performance:** Processa menos pixels
- **Precisão:** Foca em área relevante
- **Custo:** Menos processamento = menos CPU

### Implementação
```python
if camera.roi_areas:
    x1, y1, x2, y2 = camera.roi_areas[0]
    frame = frame[y1:y2, x1:x2]
    
results = model.predict(frame)
```

## Performance

### Métricas
- **Latência:** ~100-300ms por frame
- **Throughput:** 10-30 FPS por câmera
- **CPU:** ~15-25% por stream ativo
- **Memória:** ~200-500MB por processo

### Otimizações Aplicadas

#### 1. Frame Skipping
```python
FRAME_SKIP = 3  # Processa 33% dos frames
```
**Economia:** 66% de CPU

#### 2. Modelo Nano (YOLOv8n)
```python
model = YOLO('yolov8n.pt')  # Menor modelo
```
**Economia:** 70% vs YOLOv8x

#### 3. CPU-Only (sem GPU)
```python
device = 'cpu'  # Sem necessidade de GPU cara
```
**Economia:** $500-2000/mês em cloud

#### 4. Batch Processing
```python
# Processa múltiplos frames juntos
results = model.predict(frames_batch)
```
**Ganho:** 30% mais rápido

## Tipos de Câmeras

### RTSP (LPR) - Alta Definição
- **IA:** ✅ Ativa
- **Resolução:** 1080p+
- **FPS:** 15-30
- **Quantidade:** 10-20 por cidade

### RTMP (Bullets) - Padrão
- **IA:** ❌ Desativada
- **Resolução:** 720p
- **FPS:** 15
- **Quantidade:** até 1000 por cidade

## API de Detecção

### Habilitar/Desabilitar IA
```typescript
// Frontend
cameraService.update(cameraId, { ai_enabled: true })
```

```python
# Backend
camera.ai_enabled = True
camera.save()
# Notifica serviço LPR via RabbitMQ
```

### Configurar Detecção
```typescript
// Frontend - DetectionConfig component
<DetectionConfig 
  camera={camera}
  onClose={() => setShowDetectionConfig(null)}
/>
```

## Armazenamento de Detecções

### Modelo
```python
class Detection(models.Model):
    camera = models.ForeignKey(Camera)
    plate_number = models.CharField(max_length=10)
    confidence = models.FloatField()
    timestamp = models.DateTimeField()
    image_url = models.CharField(max_length=1000)
    vehicle_type = models.CharField(max_length=50)
```

### Índices
```python
class Meta:
    indexes = [
        models.Index(fields=['plate_number', 'timestamp']),
        models.Index(fields=['camera', 'timestamp']),
    ]
```

## Sentinela (Busca Retroativa)

### Conceito
Busca em gravações passadas (não tempo real).

### Casos de Uso
- Buscar placa específica
- Buscar por cor/tipo de veículo
- Buscar por período
- Buscar por câmera

### Implementação (Futuro)
```python
# Processa gravação offline
def search_recordings(plate_number, start_date, end_date):
    recordings = get_recordings(start_date, end_date)
    
    for recording in recordings:
        frames = extract_frames(recording)
        detections = process_frames(frames)
        
        if plate_number in detections:
            yield detection
```

## Troubleshooting

### Baixa Precisão
- Ajustar confidence threshold
- Melhorar iluminação da câmera
- Definir ROI mais preciso
- Aumentar resolução

### Alto Uso de CPU
- Aumentar frame_skip
- Reduzir resolução
- Usar ROI menor
- Limitar câmeras simultâneas

### Detecções Duplicadas
- Implementar deduplicação temporal
- Aumentar intervalo entre detecções
- Usar tracking de objetos

## Próximos Passos

- [ ] Tracking de veículos (evitar duplicatas)
- [ ] Suporte a placas Mercosul
- [ ] Detecção de cor de veículo
- [ ] Detecção de tipo de veículo
- [ ] API de busca retroativa (Sentinela)
- [ ] Dashboard de estatísticas
- [ ] Alertas em tempo real

---

**Ver também:**
- [Performance](../performance/AI_OPTIMIZATION.md)
- [Cost Optimization](../cost-optimization/CPU_USAGE.md)
- [Backend Integration](../backend/LPR_SERVICE.md)
