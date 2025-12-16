# GT-Vision AI Service

Microsserviço isolado de IA para detecção de veículos, placas (LPR) e classificação de modelos.

## 🎯 Características

- **YOLO v8** para detecção de veículos
- **TensorFlow** para LPR e classificação de modelos
- **Redis** para fila assíncrona (suporta 250+ câmeras)
- **FastAPI** com endpoints síncronos e assíncronos
- **Prometheus** para métricas
- **GPU support** (NVIDIA CUDA)

## 🚀 Quick Start

### 1. Configuração

```bash
cp .env.example .env
# Edite .env conforme necessário
```

### 2. Iniciar com Docker

```bash
docker-compose up -d
```

### 3. Testar

```bash
pip install requests opencv-python numpy
python test_client.py
```

## 📡 API Endpoints

### Health Check
```bash
GET /health
```

### Detecção Síncrona
```bash
POST /detect
{
  "camera_id": 1,
  "image_base64": "base64_encoded_image"
}
```

### Detecção Assíncrona
```bash
POST /detect/async
{
  "camera_id": 1,
  "image_base64": "base64_encoded_image"
}

# Retorna task_id, depois consultar:
GET /result/{task_id}
```

### Upload de Arquivo
```bash
POST /detect/upload?camera_id=1
Content-Type: multipart/form-data
file: image.jpg
```

### Métricas Prometheus
```bash
GET /metrics
```

## 📊 Performance

- **Throughput**: ~250 detecções/segundo (4 workers, GPU)
- **Latência**: <100ms por frame (GPU), <500ms (CPU)
- **Queue**: Suporta 1000 tarefas pendentes

## 🔧 Configuração Avançada

### Ajustar Workers
```env
WORKERS=8  # Aumentar para mais throughput
```

### GPU Memory
```env
GPU_MEMORY_FRACTION=0.8  # Ajustar conforme VRAM disponível
```

### Confidence Threshold
```env
CONFIDENCE_THRESHOLD=0.5  # Aumentar para menos falsos positivos
```

## 📦 Modelos

Coloque seus modelos treinados em `./models/`:

- `lpr_model.h5` - Modelo de reconhecimento de placas
- `vehicle_classifier.h5` - Classificador de modelos de veículos

Se não existirem, o serviço usa placeholders.

## 🔗 Integração com Backend Principal

```python
import requests
import base64

# Enviar frame para detecção
with open("frame.jpg", "rb") as f:
    img_b64 = base64.b64encode(f.read()).decode()

response = requests.post("http://ai-service:8000/detect", json={
    "camera_id": 1,
    "image_base64": img_b64
})

detections = response.json()["detections"]
for det in detections:
    print(f"{det['object_type']}: {det['confidence']:.2f}")
    if det['plate_number']:
        print(f"  Placa: {det['plate_number']}")
    if det['vehicle_model']:
        print(f"  Modelo: {det['vehicle_model']}")
```

## 📈 Monitoramento

Métricas disponíveis em `http://localhost:9090/metrics`:

- `detections_processed_total` - Total de detecções processadas
- `detection_processing_seconds` - Histograma de tempo de processamento
- `detection_queue_size` - Tamanho atual da fila

## 🐛 Troubleshooting

### GPU não detectada
```bash
# Verificar NVIDIA drivers
nvidia-smi

# Verificar TensorFlow GPU
docker exec -it gtvision-ai python -c "import tensorflow as tf; print(tf.config.list_physical_devices('GPU'))"
```

### Alta latência
- Aumentar `WORKERS`
- Reduzir `CONFIDENCE_THRESHOLD`
- Usar modelo YOLO menor (yolov8n.pt)

### Queue cheia
- Aumentar `MAX_QUEUE_SIZE`
- Adicionar mais workers
- Otimizar processamento downstream
