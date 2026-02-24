# Otimização de Armazenamento VMS

## Análise Atual
- **Resolução**: 2688x1520 (2K+)
- **Bitrate**: 4 Mbps (~30 MB/min)
- **Codec**: H.264 (copy - sem recompressão)
- **Uso**: 34 GB/dia por câmera

## ✅ Soluções Recomendadas (Ordem de Prioridade)

### 1. Re-encoding com CRF 23 (Melhor Custo-Benefício)
**Redução: 40-50% | Qualidade: Imperceptível**

```python
# recorder.py
cmd = [
    "ffmpeg", "-y",
    "-rtsp_transport", "tcp",
    "-i", self.mediamtx_url,
    "-c:v", "libx264",
    "-crf", "23",           # Qualidade constante (18=alta, 23=ótima, 28=boa)
    "-preset", "faster",    # Velocidade de encoding
    "-tune", "zerolatency", # Otimiza para streaming
    "-g", "60",             # Keyframe a cada 2s (30fps)
    "-an",
    "-f", "segment",
    "-segment_time", "60",
    "-segment_format", "mp4",
    "-reset_timestamps", "1",
    "-strftime", "1",
    output_path
]
```

**Resultado**: 17-20 GB/dia por câmera
**Total 3 câmeras**: ~900 GB (em vez de 1.77 TB)

---

### 2. Resolução 1080p (Mantém Qualidade Visual)
**Redução: 30-40% | Qualidade: Excelente**

```python
cmd = [
    "ffmpeg", "-y",
    "-rtsp_transport", "tcp",
    "-i", self.mediamtx_url,
    "-c:v", "libx264",
    "-crf", "23",
    "-preset", "faster",
    "-vf", "scale=1920:1080",  # Reduz de 2688x1520 para 1920x1080
    "-an",
    "-f", "segment",
    "-segment_time", "60",
    "-segment_format", "mp4",
    "-reset_timestamps", "1",
    "-strftime", "1",
    output_path
]
```

**Resultado**: 20-24 GB/dia por câmera
**Total 3 câmeras**: ~1.1 TB

---

### 3. Codec H.265 (HEVC) - Melhor Compressão
**Redução: 50-60% | Qualidade: Idêntica ao H.264**

```python
cmd = [
    "ffmpeg", "-y",
    "-rtsp_transport", "tcp",
    "-i", self.mediamtx_url,
    "-c:v", "libx265",
    "-crf", "28",           # H.265 usa CRF mais alto (28 = qualidade similar a H.264 CRF 23)
    "-preset", "fast",
    "-tag:v", "hvc1",       # Compatibilidade com players
    "-an",
    "-f", "segment",
    "-segment_time", "60",
    "-segment_format", "mp4",
    "-reset_timestamps", "1",
    "-strftime", "1",
    output_path
]
```

**Resultado**: 13-17 GB/dia por câmera
**Total 3 câmeras**: ~700 GB

⚠️ **Atenção**: H.265 requer mais CPU para encoding

---

### 4. Estratégia Híbrida (RECOMENDADO) ⭐
**Redução: 60% | Qualidade: Ótima onde importa**

#### Configuração por Período:
- **Dias 1-7**: 1080p, CRF 23, H.264 (qualidade alta)
- **Dias 8-30**: 720p, CRF 25, H.264 (qualidade boa)

```python
# Implementar em recorder.py
def get_encoding_params(self, days_old=0):
    if days_old <= 7:
        return {
            "scale": "1920:1080",
            "crf": "23",
            "preset": "faster"
        }
    else:
        return {
            "scale": "1280:720",
            "crf": "25",
            "preset": "fast"
        }
```

**Resultado**: 
- Câmera 7 dias: 140 GB (20 GB/dia)
- Câmera 15 dias: 240 GB (7 dias alta + 8 dias média)
- Câmera 30 dias: 450 GB (7 dias alta + 23 dias média)
**Total**: ~830 GB

---

## 🎯 Recomendação Final

### Opção 1: Simples e Eficaz
**CRF 23 + 1080p + H.264**
- Redução: 50%
- Armazenamento: 1.1 TB
- CPU: Baixo
- Compatibilidade: 100%

### Opção 2: Máxima Economia
**CRF 28 + 1080p + H.265**
- Redução: 60%
- Armazenamento: 700 GB
- CPU: Médio
- Compatibilidade: 95%

### Opção 3: Melhor Custo-Benefício (ESCOLHA ESTA) ⭐
**CRF 23 + Resolução Original + H.264**
- Redução: 40%
- Armazenamento: 1.06 TB
- CPU: Baixo
- Qualidade: Praticamente idêntica ao original

---

## Comparação de Qualidade

| Método | Tamanho | Qualidade Visual | CPU | Compatibilidade |
|--------|---------|------------------|-----|-----------------|
| Copy (atual) | 1.77 TB | 100% | 0% | 100% |
| CRF 23 H.264 | 1.06 TB | 98% | 20% | 100% |
| CRF 23 + 1080p | 900 GB | 95% | 20% | 100% |
| CRF 28 H.265 | 700 GB | 95% | 60% | 95% |
| Híbrida | 830 GB | 97% | 20% | 100% |

---

## Implementação Rápida

### Arquivo: `services/recorder/recorder.py`

```python
# Substituir o cmd atual por:
cmd = [
    "ffmpeg", "-y",
    "-rtsp_transport", "tcp",
    "-timeout", "5000000",
    "-i", self.mediamtx_url,
    "-c:v", "libx264",
    "-crf", "23",
    "-preset", "faster",
    "-tune", "zerolatency",
    "-g", "60",
    "-an",
    "-f", "segment",
    "-segment_time", "60",
    "-segment_format", "mp4",
    "-reset_timestamps", "1",
    "-strftime", "1",
    output_path
]
```

### Testar Qualidade
```bash
# Gravar 1 minuto com copy
# Gravar 1 minuto com CRF 23
# Comparar visualmente

docker exec gtvision_recorder ls -lh /recordings/camera_7/2026-02-23/
```

---

## Monitoramento de CPU

```bash
# Verificar uso de CPU do recorder
docker stats gtvision_recorder --no-stream
```

Se CPU > 80%, aumentar preset:
- `ultrafast` (mais CPU, menos compressão)
- `faster` (balanceado) ⭐
- `fast` (menos CPU, mais compressão)
