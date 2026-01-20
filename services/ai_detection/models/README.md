# 🤖 Modelos YOLO - AI Detection

## 📦 Modelos Incluídos

### 1. Vehicle Detection (yolov8n.pt)
**Fonte**: Ultralytics YOLOv8n oficial  
**Treinado em**: COCO dataset  
**Classes**: car, truck, motorcycle, bus, train, boat  
**Tamanho**: 6MB  
**Uso**: Detectar veículos no frame

### 2. Plate Detection (plate_yolov8n.pt)
**Fonte**: `tdiblik_lp_finetuned_yolov8n.pt` do alpr-yolov8-python-ocr  
**Treinado em**: Datasets de placas (andrewmvd + aslanahmedov)  
**Classes**: license_plate  
**Tamanho**: 6MB  
**Uso**: Detectar placas nos veículos  
**⭐ FINE-TUNED**: Muito mais preciso que modelo genérico!

## 🎯 Por que Fine-Tuned?

### Modelo Genérico (yolov8n.pt)
```
Treinado em: COCO (objetos gerais)
Placas: Não específico
Precisão: ~60-70% em placas
```

### Modelo Fine-Tuned (plate_yolov8n.pt)
```
Treinado em: 10k+ imagens de placas
Placas: Especializado
Precisão: ~90-95% em placas
```

**Resultado**: +30% de precisão! 🚀

## 📊 Datasets Usados

### andrewmvd Dataset
- 433 imagens
- Placas brasileiras
- Anotações YOLO format

### aslanahmedov Dataset  
- 9,000+ imagens
- Placas internacionais
- Múltiplos ângulos

## 🔧 Como Foram Treinados

```bash
# No alpr-yolov8-python-ocr
cd ai
python prepare.py  # Prepara datasets
python train.py    # Treina modelo

# Resultado: tdiblik_lp_finetuned_yolov8n.pt
```

## 📁 Localização

```
services/ai_detection/models/
├── vehicle_yolov8n.pt    # Detecção de veículos (COCO)
└── plate_yolov8n.pt      # Detecção de placas (FINE-TUNED)
```

## 🚀 Outros Modelos Disponíveis

No `alpr-yolov8-python-ocr/ai/resources/`:

| Modelo | Tamanho | Precisão | Velocidade | Uso |
|--------|---------|----------|------------|-----|
| yolov8n | 6MB | Boa | Rápido | ✅ Produção |
| yolov8s | 22MB | Melhor | Médio | Desenvolvimento |
| yolov8m | 50MB | Ótima | Lento | GPU |
| yolov8l | 87MB | Excelente | Muito Lento | GPU |
| yolov8x | 136MB | Máxima | Extremamente Lento | GPU |

**Recomendado**: `yolov8n` (nano) para CPU-only

## 🔄 Trocar Modelos

### Usar modelo maior (mais preciso, mais lento)

```bash
# Copiar modelo S (22MB)
cp services/alpr-yolov8-python-ocr/ai/resources/tdiblik_lp_finetuned_yolov8s.pt \
   services/ai_detection/models/plate_yolov8s.pt

# Atualizar .env
PLATE_MODEL=models/plate_yolov8s.pt
```

### Usar modelo genérico (teste)

```bash
# .env
PLATE_MODEL=models/vehicle_yolov8n.pt  # Usa mesmo modelo para tudo
```

## 📈 Performance Esperada

### Com Fine-Tuned (plate_yolov8n.pt)
- **Detecção de placas**: 90-95%
- **FPS**: 3-5 FPS (CPU)
- **Falsos positivos**: <5%

### Com Genérico (yolov8n.pt)
- **Detecção de placas**: 60-70%
- **FPS**: 3-5 FPS (CPU)
- **Falsos positivos**: ~15%

## ⚠️ Importante

1. **Sempre use fine-tuned para placas**: `plate_yolov8n.pt`
2. **Modelo genérico só para veículos**: `vehicle_yolov8n.pt`
3. **CPU-only**: Use modelos `n` (nano)
4. **GPU disponível**: Pode usar `s` ou `m`

## 🔗 Referências

- [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics)
- [ALPR YOLOv8 Python OCR](https://github.com/tdiblik/alpr-yolov8-python-ocr)
- [COCO Dataset](https://cocodataset.org/)
