# 🤖 Modelos YOLO Treinados

## 📁 Estrutura

Coloque seus modelos YOLO treinados nesta pasta:

```
models/
├── yolov8n.pt              # Modelo base (detecção de veículos)
├── yolov8n_plates.pt       # Modelo treinado para placas (se houver)
└── README.md               # Este arquivo
```

---

## 📥 Como Adicionar Modelo

### 1. Copiar modelo para esta pasta

```bash
# Windows
copy C:\path\to\your\yolov8n.pt d:\VMS\vms\src\lpr\infrastructure\yolo\models\

# Linux/Mac
cp /path/to/your/yolov8n.pt /VMS/vms/src/lpr/infrastructure/yolo/models/
```

### 2. Configurar no provider

O modelo será carregado automaticamente pelo `YOLODetectionProvider`:

```python
# infrastructure/yolo/detection_provider.py
from ultralytics import YOLO

class YOLODetectionProvider:
    def __init__(self, model_path: str = None):
        if model_path is None:
            # Usa modelo padrão
            model_path = Path(__file__).parent / 'models' / 'yolov8n.pt'
        
        self.model = YOLO(model_path)
```

---

## 🎯 Modelos Recomendados

### YOLOv8n (Nano)
- **Tamanho:** ~6MB
- **Velocidade:** ~100 FPS (CPU)
- **Uso:** Detecção de veículos
- **Download:** https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt

### YOLOv8s (Small)
- **Tamanho:** ~22MB
- **Velocidade:** ~50 FPS (CPU)
- **Uso:** Melhor precisão
- **Download:** https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8s.pt

---

## ⚙️ Configuração

### Variáveis de Ambiente

```bash
# .env
YOLO_MODEL_PATH=/path/to/models/yolov8n.pt
YOLO_CONFIDENCE_THRESHOLD=0.75
YOLO_DEVICE=cpu  # ou 'cuda' para GPU
```

### Settings Django

```python
# config/settings.py
YOLO_CONFIG = {
    'model_path': os.getenv('YOLO_MODEL_PATH', 'models/yolov8n.pt'),
    'confidence': float(os.getenv('YOLO_CONFIDENCE_THRESHOLD', 0.75)),
    'device': os.getenv('YOLO_DEVICE', 'cpu'),
}
```

---

## 🔧 Treinar Modelo Customizado

Se você tem um dataset de placas brasileiras:

```python
from ultralytics import YOLO

# Carregar modelo base
model = YOLO('yolov8n.pt')

# Treinar com seu dataset
model.train(
    data='plates_dataset.yaml',
    epochs=100,
    imgsz=640,
    batch=16,
    device='cpu'
)

# Salvar modelo treinado
model.save('models/yolov8n_plates.pt')
```

---

## 📊 Performance

### CPU-only (Recomendado)
- **YOLOv8n:** ~100 FPS
- **Processamento:** 1 frame a cada 3 (3 FPS efetivo)
- **Custo:** $0 (sem GPU)

### Com GPU (Opcional)
- **YOLOv8n:** ~500 FPS
- **Custo:** ~$500/mês (GPU cloud)

---

## ⚠️ Importante

1. **Não commitar modelos** no Git (são grandes)
2. **Adicionar ao .gitignore:**
   ```
   *.pt
   *.pth
   *.onnx
   ```
3. **Usar volume Docker** para modelos em produção

---

## 🚀 Uso

```python
# Carregar modelo
provider = YOLODetectionProvider(
    model_path='models/yolov8n.pt'
)

# Detectar placas
results = provider.detect_plates(frame)
```
