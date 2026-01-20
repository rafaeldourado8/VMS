# Quality Scorer

## 📝 O que é

Avalia qualidade de cada frame para selecionar os melhores para OCR, maximizando precisão de leitura de placas.

## 🎯 Função

Calcula score (0-100) baseado em 4 métricas: nitidez, ângulo, contraste e tamanho da placa.

## 📊 Input/Output

**Input**: 
- Frames do Track Buffer (10-30 frames por veículo)
- Bounding box do veículo

**Output**:
- Score de qualidade (0-100)
- Breakdown por métrica
- Ranking de frames

## 🔧 Como Funciona

### 1. Blur Detection (Laplacian Variance)

**O que mede**: Nitidez do frame

```python
import cv2
import numpy as np

def calculate_blur_score(frame):
    # Converte para escala de cinza
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Calcula variância do Laplacian
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    variance = laplacian.var()
    
    # Normaliza para 0-100
    # Variance > 500 = nítido (score alto)
    # Variance < 100 = borrado (score baixo)
    score = min(100, (variance / 500) * 100)
    
    return score
```

**Thresholds**:
- Excelente: variance > 500 (score 100)
- Bom: variance 200-500 (score 40-100)
- Ruim: variance < 100 (score < 20)

---

### 2. Angle Detection (Perspectiva da Placa)

**O que mede**: Ângulo frontal da placa

```python
def calculate_angle_score(bbox, frame_width):
    x1, y1, x2, y2 = bbox
    center_x = (x1 + x2) / 2
    frame_center = frame_width / 2
    
    # Distância do centro (0 = frontal, 1 = lateral)
    offset = abs(center_x - frame_center) / frame_center
    
    # Score: frontal = 100, lateral = 0
    score = (1 - offset) * 100
    
    return score
```

**Thresholds**:
- Frontal: offset < 0.2 (score > 80)
- Diagonal: offset 0.2-0.5 (score 50-80)
- Lateral: offset > 0.5 (score < 50)

---

### 3. Contrast Detection (Histograma)

**O que mede**: Diferença entre claro/escuro

```python
def calculate_contrast_score(frame):
    # Converte para escala de cinza
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Calcula histograma
    hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
    
    # Calcula desvio padrão (spread do histograma)
    std = np.std(hist)
    
    # Normaliza para 0-100
    # Alto contraste = std alto = score alto
    score = min(100, (std / 50) * 100)
    
    return score
```

**Thresholds**:
- Alto contraste: std > 50 (score 100)
- Médio contraste: std 20-50 (score 40-100)
- Baixo contraste: std < 20 (score < 40)

---

### 4. Size Detection (Tamanho da Placa)

**O que mede**: Área da placa em pixels

```python
def calculate_size_score(bbox, min_size=2000, max_size=50000):
    x1, y1, x2, y2 = bbox
    width = x2 - x1
    height = y2 - y1
    area = width * height
    
    # Normaliza entre min e max
    if area < min_size:
        score = (area / min_size) * 50
    elif area > max_size:
        score = 50
    else:
        score = 50 + ((area - min_size) / (max_size - min_size)) * 50
    
    return score
```

**Thresholds**:
- Ideal: 10k-30k pixels (score 80-100)
- Aceitável: 5k-10k pixels (score 50-80)
- Pequeno: < 5k pixels (score < 50)

---

### 5. Score Final (Weighted Average)

```python
def calculate_final_score(blur, angle, contrast, size):
    # Pesos configuráveis
    weights = {
        'blur': 0.35,      # Mais importante (nitidez)
        'angle': 0.30,     # Muito importante (frontal)
        'contrast': 0.20,  # Importante (legibilidade)
        'size': 0.15       # Menos importante (zoom)
    }
    
    final = (
        blur * weights['blur'] +
        angle * weights['angle'] +
        contrast * weights['contrast'] +
        size * weights['size']
    )
    
    return final
```

## ⚙️ Configuração

### Variáveis de Ambiente

```bash
# Pesos das métricas (soma = 1.0)
QUALITY_WEIGHT_BLUR=0.35
QUALITY_WEIGHT_ANGLE=0.30
QUALITY_WEIGHT_CONTRAST=0.20
QUALITY_WEIGHT_SIZE=0.15

# Thresholds
BLUR_MIN_VARIANCE=100
BLUR_GOOD_VARIANCE=500
CONTRAST_MIN_STD=20
CONTRAST_GOOD_STD=50
SIZE_MIN_PIXELS=2000
SIZE_MAX_PIXELS=50000

# Score mínimo para processar
MIN_QUALITY_SCORE=50
```

### Exemplo de Uso

```python
from core.quality_scorer import QualityScorer

scorer = QualityScorer(
    blur_weight=0.35,
    angle_weight=0.30,
    contrast_weight=0.20,
    size_weight=0.15
)

# Avalia frame
result = scorer.score(frame, vehicle_bbox)

print(f"Score Final: {result.final_score}")
print(f"  Blur: {result.blur_score}")
print(f"  Angle: {result.angle_score}")
print(f"  Contrast: {result.contrast_score}")
print(f"  Size: {result.size_score}")

# Seleciona melhores frames
frames_ranked = scorer.rank_frames(track_frames)
best_frames = frames_ranked[:3]  # Top 3
```

## 📈 Performance

### Distribuição de Scores (Típica)

```
Score Range    % Frames    Qualidade
0-30           10%         Ruim (descartar)
30-50          20%         Baixa (usar se necessário)
50-70          40%         Média (aceitável)
70-85          20%         Boa (preferível)
85-100         10%         Excelente (ideal)
```

### Impacto na Precisão OCR

| Score Range | OCR Accuracy | Consensus Rate |
|-------------|--------------|----------------|
| 85-100 | 98% | 95% |
| 70-85 | 92% | 85% |
| 50-70 | 80% | 65% |
| 30-50 | 60% | 40% |
| 0-30 | 30% | 10% |

**Recomendação**: Usar apenas frames com score > 50

## 🎨 Visualização

### Debug Mode

```python
scorer = QualityScorer(debug=True)

# Gera imagem com overlay:
# - Score total
# - Breakdown por métrica
# - Bounding box colorido por qualidade
#   - Verde: score > 70
#   - Amarelo: score 50-70
#   - Vermelho: score < 50
```

### Exemplo Visual

```
┌─────────────────────────┐
│  Score: 87.5            │
│  ┌─────────────┐        │
│  │   🚗        │        │
│  │  [ABC1234]  │        │
│  └─────────────┘        │
│                         │
│  Blur:     92 ████████  │
│  Angle:    85 ███████   │
│  Contrast: 88 ████████  │
│  Size:     84 ███████   │
└─────────────────────────┘
```

## 🔍 Por que essas métricas?

### Blur (Nitidez)
- **Problema**: Frame borrado = OCR falha
- **Causa**: Movimento rápido, foco ruim
- **Solução**: Laplacian detecta bordas nítidas

### Angle (Ângulo)
- **Problema**: Placa lateral = caracteres distorcidos
- **Causa**: Veículo não está frontal
- **Solução**: Posição no frame indica ângulo

### Contrast (Contraste)
- **Problema**: Baixo contraste = difícil separar caracteres
- **Causa**: Iluminação ruim, placa suja
- **Solução**: Histograma mede distribuição de tons

### Size (Tamanho)
- **Problema**: Placa pequena = poucos pixels por caractere
- **Causa**: Veículo longe da câmera
- **Solução**: Área da bbox indica proximidade

## ⚠️ Considerações

### Cenários Desafiadores

1. **Noite (baixa iluminação)**
   - Blur score baixo (ruído)
   - Contrast score baixo
   - Solução: Reduzir peso de blur (0.25)

2. **Chuva (gotas na lente)**
   - Blur score baixo (distorção)
   - Solução: Aumentar peso de angle (0.35)

3. **Contraluz (sol atrás do veículo)**
   - Contrast score baixo (silhueta)
   - Solução: Aumentar peso de size (0.25)

4. **Veículo em alta velocidade**
   - Blur score baixo (motion blur)
   - Solução: Aumentar FPS de captura

### Troubleshooting

**Problema**: Todos os scores baixos
```bash
# Verificar iluminação da câmera
# Ajustar exposição/ganho

# Reduzir threshold mínimo
MIN_QUALITY_SCORE=40
```

**Problema**: Frames laterais sendo escolhidos
```bash
# Aumentar peso do ângulo
QUALITY_WEIGHT_ANGLE=0.40
QUALITY_WEIGHT_BLUR=0.30
```

**Problema**: Frames borrados sendo escolhidos
```bash
# Aumentar peso do blur
QUALITY_WEIGHT_BLUR=0.45
QUALITY_WEIGHT_ANGLE=0.25
```

## 📊 Métricas

### Monitoramento

```python
# Métricas exportadas para Prometheus
quality_score_avg          # Score médio dos frames
quality_score_distribution # Histograma de scores
quality_blur_avg           # Blur médio
quality_angle_avg          # Angle médio
quality_contrast_avg       # Contrast médio
quality_size_avg           # Size médio
quality_processing_time    # Tempo de cálculo (ms)
```

### Alertas

```yaml
# Alerta se scores muito baixos
- alert: LowQualityFrames
  expr: quality_score_avg < 50
  annotations:
    summary: "Qualidade média dos frames < 50"
    
# Alerta se muito blur
- alert: HighBlurRate
  expr: quality_blur_avg < 40
  annotations:
    summary: "Frames muito borrados (blur < 40)"
```

## 🔗 Relacionado

- [Track Buffer](./TRACK_BUFFER.md) - Componente anterior
- [Best Frame Selection](./BEST_FRAME.md) - Próximo componente
- [OCR Engine](./OCR_ENGINE.md) - Usa os melhores frames
- [Pipeline Overview](../README.md#pipeline-de-processamento) - Visão geral
