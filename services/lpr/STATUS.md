# Status do Sistema LPR

## ✅ Funcionando

1. **Detecção de Placas**: YOLO detecta placas com sucesso
2. **Salvamento de Snapshots**: Gera pastas com UUID único
3. **Metadados**: JSON com bbox, confidence, timestamp
4. **Múltiplas Câmeras**: Processa várias câmeras simultaneamente
5. **Imagens**: Salva `vehicle.jpg`, `plate.jpg`, `full_frame.jpg`

## ⚠️ Problema Atual

**OCR não extrai texto das placas** (`plate_text: null`)

### Causa
PaddleOCR tem erro interno: `ConvertPirAttribute2RuntimeAttribute not support`

### Soluções Possíveis

1. **EasyOCR** (Recomendado)
   - Mais simples e estável
   - Melhor para placas
   - Adicionar ao requirements.txt: `easyocr`

2. **Tesseract OCR**
   - Mais leve
   - Requer instalação sistema
   
3. **API Externa**
   - OpenALPR
   - PlateRecognizer

## 📊 Estatísticas Atuais

- Câmera 555: ~200 detecções
- Câmera 777: ~600 detecções  
- Câmera 888: ~50 detecções
- Câmera 999: ~700 detecções

Total: **~1550 placas detectadas** (sem texto extraído)

## 🔧 Para Implementar EasyOCR

```python
# requirements.txt
easyocr

# lpr_stream_simple.py
import easyocr
reader = easyocr.Reader(['en'], gpu=True if torch.cuda.is_available() else False)

def _extract_plate_text(self, plate_img):
    result = reader.readtext(plate_img)
    texts = [text for (bbox, text, conf) in result if conf > 0.5]
    return ''.join(texts).upper().replace(' ', '')
```

## 📁 Estrutura Atual dos Snapshots

```
snapshots/cam_XXX/TIMESTAMP_UUID/
├── vehicle.jpg      ✅
├── plate.jpg        ✅  
├── full_frame.jpg   ✅
└── metadata.json    ✅ (sem plate_text)
```

## 🎯 Próximos Passos

1. Substituir PaddleOCR por EasyOCR
2. Ajustar pré-processamento da imagem (contraste, binarização)
3. Adicionar validação de formato de placa
4. Integrar com banco de dados
5. API para consulta de detecções
