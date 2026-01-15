# 🧪 Teste LPR - Detecção de Placas

## 📋 Objetivo
Testar o pipeline completo de detecção de placas (YOLO + OCR) usando imagens estáticas.

## 🚀 Como Usar

### 1. Adicionar Imagens
Coloque imagens de carros com placas visíveis nesta pasta:
```
ai-services/ai/teste_lpr/
├── carro1.jpg
├── carro2.jpg
└── carro3.png
```

### 2. Executar Teste
```bash
cd ai-services/ai/teste_lpr
python test_lpr.py
```

### 3. Ver Resultados
Os resultados são salvos em `results/`:
```
results/
├── carro1_v0_p0_vehicle.jpg  # Imagem do veículo
├── carro1_v0_p0_plate.jpg    # Imagem da placa
└── ...
```

## 📊 Output Esperado

```
🚗 Teste LPR - Detecção de Placas
==================================================

📦 Carregando modelos...
✅ Modelos carregados

📸 Encontradas 3 imagens
==================================================

🔍 Processando: carro1.jpg
   Veículos detectados: 1
   Placas detectadas no veículo 1: 1
   ✅ PLACA DETECTADA: ABC1D23
      Salvo em: results/carro1_v0_p0_*.jpg

🔍 Processando: carro2.jpg
   Veículos detectados: 2
   Placas detectadas no veículo 1: 1
   ✅ PLACA DETECTADA: XYZ9876
      Salvo em: results/carro2_v0_p0_*.jpg

==================================================
🎯 Total de placas detectadas: 2
📁 Resultados salvos em: results/
==================================================
```

## 🔧 Requisitos

- Python 3.11+
- ultralytics
- opencv-python-headless
- pytesseract
- Pillow
- imutils
- scikit-image

## 📝 Notas

- Usa modelo base YOLOv8n (não fine-tuned)
- Para melhor precisão, use modelo fine-tuned para placas
- Tesseract deve estar instalado no sistema
- Funciona com .jpg e .png

## 🐛 Troubleshooting

### Nenhuma placa detectada
- Verificar qualidade da imagem
- Placa deve estar visível e legível
- Testar com imagens de melhor resolução

### Erro no Tesseract
```bash
# Windows
choco install tesseract

# Linux
sudo apt-get install tesseract-ocr tesseract-ocr-eng
```

### Modelo não encontrado
O script baixa automaticamente o yolov8n.pt na primeira execução.
