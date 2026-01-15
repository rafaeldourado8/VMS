# 🚗 LPR Mercosul Gateway

Gateway adaptado do [alpr-yolov8-python-ocr](https://github.com/tdiblik/alpr-yolov8-python-ocr) para o VMS.

## 🎯 Características

- **YOLO Fine-tuned**: Usa modelos treinados do alpr-yolov8
- **Tesseract OCR**: Reconhecimento de caracteres otimizado
- **Multi-round Validation**: Valida detecções em 3 rounds
- **Media Storage**: Salva imagens em pasta local
- **Backend Integration**: Envia detecções para o VMS backend

## 📦 Setup

### 1. Copiar modelos do alpr-yolov8-python-ocr

```bash
# No diretório alpr-yolov8-python-ocr/ai/resources
cat yolov8n_* > yolov8n.pt
cat tdiblik_lp_finetuned_yolov8n_* > tdiblik_lp_finetuned_yolov8n.pt

# Copiar para services/lpr_mercosul/models/
cp yolov8n.pt ../../services/lpr_mercosul/models/
cp tdiblik_lp_finetuned_yolov8n.pt ../../services/lpr_mercosul/models/plate_yolov8n.pt
```

### 2. Configurar .env

```bash
cp .env.example .env
# Editar ADMIN_API_KEY
```

### 3. Iniciar serviço

```bash
docker-compose up -d lpr_mercosul
```

## 🏗️ Arquitetura

```
RTSP Camera → Frame Capture → YOLO Vehicle Detection
                                      ↓
                              YOLO Plate Detection
                                      ↓
                              Tesseract OCR
                                      ↓
                              Multi-round Validation
                                      ↓
                              Save to Media + Send to Backend
```

## 📊 Fluxo de Detecção

1. **Captura**: Lê frames RTSP (com frame skip)
2. **Detecção Veículo**: YOLO detecta carros/motos/caminhões
3. **Filtro Distância**: Ignora veículos muito longe (y_max < threshold)
4. **Detecção Placa**: YOLO fine-tuned detecta placas no veículo
5. **OCR**: Tesseract lê caracteres da placa
6. **Validação**: Valida em 3 rounds (mínimo 2 ocorrências)
7. **Deduplicação**: Ignora placas detectadas nos últimos 5 minutos
8. **Persistência**: Salva imagens em `media/detections/`
9. **Backend**: Envia detecção para API do VMS

## 🎛️ Configuração

### Frame Skip
- `FRAME_SKIP=3`: Processa 1 a cada 3 frames
- Reduz CPU em 66%

### Skip Y Threshold
- `SKIP_Y_THRESHOLD=100.0`: Ignora veículos com y_max < 100
- Melhora precisão ignorando veículos distantes

### Validation Rounds
- `VALIDATION_ROUNDS=3`: Valida em 3 rounds
- `MIN_OCCURRENCES=2`: Placa deve aparecer 2x para ser válida
- Reduz falsos positivos

### Min Chars
- `MIN_CHARS=4`: Mínimo 4 caracteres para considerar válido
- Padrão Mercosul: 7 caracteres (ABC1D23)

## 📁 Estrutura de Media

```
media/detections/
├── {uuid}_vehicle.jpg  # Imagem do veículo
└── {uuid}_plate.jpg    # Imagem da placa
```

## 🔧 Modelos

### Vehicle Detection
- `yolov8n.pt`: YOLO padrão para veículos
- Classes: car, motorcycle, bus, truck

### Plate Detection
- `plate_yolov8n.pt`: YOLO fine-tuned para placas
- Treinado com datasets Mercosul

## 📝 Payload Backend

```json
{
  "camera_id": 1,
  "plate": "ABC1D23",
  "confidence": 0.85,
  "bbox": [100, 200, 300, 400],
  "timestamp": "2025-01-01T12:00:00",
  "detection_id": "uuid",
  "vehicle_image": "path/to/vehicle.jpg",
  "plate_image": "path/to/plate.jpg"
}
```

## 🐛 Troubleshooting

### Modelos não encontrados
```bash
# Verificar se modelos existem
ls -la models/
```

### Tesseract não instalado
```bash
# No container
apt-get update && apt-get install -y tesseract-ocr tesseract-ocr-eng
```

### Baixa precisão
- Ajustar `SKIP_Y_THRESHOLD` baseado na câmera
- Aumentar `VALIDATION_ROUNDS` e `MIN_OCCURRENCES`
- Usar modelo maior (yolov8m ou yolov8l)

## 📚 Créditos

Baseado em [alpr-yolov8-python-ocr](https://github.com/tdiblik/alpr-yolov8-python-ocr) por @tdiblik
