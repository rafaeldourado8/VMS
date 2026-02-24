# Calculadora de Armazenamento VMS

## Dados Reais da Câmera 7
- **Bitrate médio**: ~23.7 MB/min (71.2 MB / 3 min)
- **Codec**: H.264 copy (sem re-encoding)
- **Segmentos**: 60 segundos

## Cálculo de Armazenamento

### Por Câmera

| Período | Cálculo | Armazenamento |
|---------|---------|---------------|
| 1 hora | 23.7 MB × 60 min | **1.42 GB** |
| 1 dia | 1.42 GB × 24h | **34.1 GB** |
| 7 dias | 34.1 GB × 7 | **238.7 GB** |
| 15 dias | 34.1 GB × 15 | **511.5 GB** |
| 30 dias | 34.1 GB × 30 | **1.02 TB** |

### Cenário Solicitado

**3 câmeras com retenções diferentes:**

| Câmera | Retenção | Armazenamento |
|--------|----------|---------------|
| Câmera 1 | 7 dias | 238.7 GB |
| Câmera 2 | 15 dias | 511.5 GB |
| Câmera 3 | 30 dias | 1.02 TB |
| **TOTAL** | - | **1.77 TB** |

### Recomendações

#### Mínimo (sem margem)
- **1.8 TB** de armazenamento

#### Recomendado (margem de 20%)
- **2.2 TB** de armazenamento

#### Ideal (margem de 50% + crescimento)
- **3.0 TB** de armazenamento

## Otimizações Possíveis

### 1. Reduzir Bitrate (Re-encoding)
```bash
# CRF 23 (qualidade média)
-c:v libx264 -crf 23 -preset medium
# Redução: ~30-40% (1.24 TB total)
```

### 2. Resolução Reduzida
```bash
# 720p em vez de 1080p
-vf scale=1280:720
# Redução: ~50% (885 GB total)
```

### 3. FPS Reduzido
```bash
# 15 FPS em vez de 30 FPS
-r 15
# Redução: ~40% (1.06 TB total)
```

### 4. Retenção Escalonada
- **Dias 1-7**: Qualidade alta (1080p, 30fps)
- **Dias 8-15**: Qualidade média (720p, 15fps)
- **Dias 16-30**: Qualidade baixa (480p, 10fps)
- **Redução total**: ~60% (708 GB)

## Implementação de Limpeza Automática

O serviço `retention_cleanup.py` já está configurado para:
- Executar a cada 6 horas
- Deletar gravações antigas baseado na configuração de cada câmera
- Manter logs de limpeza

### Configuração por Câmera (Django Admin)
```python
camera.retention_days = 7  # ou 15, ou 30
```

## Monitoramento

### Verificar Uso Atual
```bash
# Windows
dir /s recordings

# Linux/Docker
du -sh /recordings/*
```

### Alertas Recomendados
- **80% de uso**: Aviso
- **90% de uso**: Crítico
- **95% de uso**: Emergência (pausar gravações)

## Custos Estimados (AWS EBS)

| Tipo | Tamanho | Custo/mês (us-east-1) |
|------|---------|----------------------|
| gp3 | 2 TB | ~$160 |
| gp3 | 3 TB | ~$240 |
| st1 (HDD) | 3 TB | ~$135 |

**Recomendação**: gp3 2TB com auto-scaling até 3TB
