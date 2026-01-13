# 💰 Cost Optimization - Estratégias de Redução de Custos

## Visão Geral

Todas as decisões tomadas para minimizar custos operacionais do VMS.

## Banda (Maior Custo)

### Problema
Streaming de vídeo consome MUITA banda:
- 1 stream HLS = ~500KB/s - 2MB/s
- 1000 câmeras = 500MB/s - 2GB/s
- 1 mês = ~1.3PB - 5.2PB
- **Custo:** $130,000 - $520,000/mês 💸

### Soluções Implementadas

#### 1. Lazy Loading (90% economia)
```typescript
// Só carrega câmeras visíveis
const observer = new IntersectionObserver(...)
```
**Economia:** $117,000 - $468,000/mês

#### 2. Screenshot Cache (95% economia após 10s)
```typescript
// Streaming por 10s, depois screenshot
setTimeout(() => {
  captureScreenshot()
  hls.destroy()
}, 10000)
```
**Economia:** $123,500 - $494,000/mês

#### 3. On-Demand Streams
```yaml
# MediaMTX só inicia stream quando necessário
runOnDemand: true
```
**Economia:** 70-90% de banda desperdiçada

#### 4. Compressão H.264
```yaml
# Codec eficiente
codec: h264
bitrate: 1000k  # Ajustável
```
**Economia:** 50% vs sem compressão

### Resultado Final
| Cenário | Banda/mês | Custo/mês |
|---------|-----------|-----------|
| Sem otimização | 5.2PB | $520,000 |
| Com otimização | 50TB | $5,000 |
| **Economia** | **99%** | **$515,000** |

## Computação (CPU/GPU)

### Problema
IA requer muito processamento:
- GPU cloud = $500-2000/mês por instância
- 10 câmeras simultâneas = 5-10 GPUs
- **Custo:** $2,500 - $20,000/mês

### Soluções Implementadas

#### 1. CPU-Only (sem GPU)
```python
device = 'cpu'
model.to(device)
```
**Economia:** $500-2000/mês por instância

#### 2. YOLOv8 Nano
```python
model = YOLO('yolov8n.pt')  # Modelo menor
```
**Economia:** 70% de CPU vs YOLOv8x

#### 3. Frame Skipping
```python
FRAME_SKIP = 3  # Processa 33% dos frames
```
**Economia:** 66% de CPU

#### 4. ROI (Region of Interest)
```python
frame = frame[y1:y2, x1:x2]  # Área menor
```
**Economia:** 50-80% de CPU

#### 5. Horizontal Scaling
```yaml
# Múltiplas instâncias CPU baratas
# ao invés de 1 GPU cara
replicas: 5
```
**Economia:** 60-80% vs GPU

### Resultado Final
| Cenário | Custo/mês |
|---------|-----------|
| GPU (10 câmeras) | $10,000 |
| CPU otimizado | $500 |
| **Economia** | **$9,500** |

## Armazenamento

### Problema
Gravações consomem muito espaço:
- 1 câmera 1080p = ~2GB/dia
- 1000 câmeras = 2TB/dia
- 30 dias = 60TB
- **Custo:** $1,200 - $6,000/mês

### Soluções Implementadas

#### 1. Gravação Cíclica
```python
# Deleta gravações antigas automaticamente
retention_days = 7  # Basic
retention_days = 15  # Pro
retention_days = 30  # Premium
```
**Economia:** 75% (7 dias vs 30 dias)

#### 2. Compressão H.264
```yaml
codec: h264
crf: 23  # Qualidade vs tamanho
```
**Economia:** 50-70% vs sem compressão

#### 3. Resolução Adaptativa
```python
# Câmeras sem IA = resolução menor
if not camera.ai_enabled:
    resolution = '720p'
else:
    resolution = '1080p'
```
**Economia:** 50% de espaço

#### 4. Clipes Seletivos
```python
# Só salva permanente quando usuário cria clipe
# Resto é deletado no ciclo
```
**Economia:** 90% de armazenamento permanente

#### 5. Storage Tiers
```python
# Gravações recentes: SSD rápido
# Gravações antigas: HDD barato
# Clipes permanentes: S3 Glacier
```
**Economia:** 70-90% vs tudo em SSD

### Resultado Final
| Cenário | Storage | Custo/mês |
|---------|---------|-----------|
| 30 dias, 1080p | 60TB | $6,000 |
| 7 dias, adaptativo | 5TB | $250 |
| **Economia** | **92%** | **$5,750** |

## Infraestrutura

### Problema
Cloud é caro:
- EC2 + RDS + S3 + Bandwidth
- **Custo:** $500-2000/mês

### Soluções Implementadas

#### 1. Self-Hosted (quando possível)
```yaml
# VPS dedicado ao invés de cloud
# Bare metal para produção
```
**Economia:** 60-80% vs cloud

#### 2. Docker (eficiência)
```yaml
# Múltiplos serviços em 1 servidor
# Melhor uso de recursos
```
**Economia:** 50% de servidores necessários

#### 3. Redis Cache
```python
# Menos queries ao DB
# DB menor necessário
```
**Economia:** 30-50% de DB size

#### 4. CDN para Assets
```nginx
# Serve assets estáticos via CDN
# Menos banda no servidor principal
```
**Economia:** 70% de banda

### Resultado Final
| Cenário | Custo/mês |
|---------|-----------|
| AWS Full Cloud | $2,000 |
| Self-hosted + CDN | $400 |
| **Economia** | **$1,600** |

## Desenvolvimento

### Problema
Tempo de dev = dinheiro

### Soluções Implementadas

#### 1. Django (batteries included)
```python
# Admin, Auth, ORM grátis
# Menos código custom
```
**Economia:** 100+ horas de dev

#### 2. TailwindCSS
```html
<!-- Sem CSS custom -->
<div class="flex items-center gap-4">
```
**Economia:** 50+ horas de dev

#### 3. React Query
```typescript
// Cache automático
// Menos código de state management
```
**Economia:** 30+ horas de dev

#### 4. Docker Compose
```yaml
# Dev environment em 1 comando
# Menos setup manual
```
**Economia:** 10+ horas por dev

## Licenciamento

### Problema
Software proprietário é caro

### Soluções Implementadas

#### 1. Open Source Stack
- Django: Free
- PostgreSQL: Free
- Redis: Free
- MediaMTX: Free
- YOLO: Free (AGPL)

**Economia:** $10,000 - $50,000/ano

#### 2. Evitar Vendor Lock-in
```python
# Não usar AWS Rekognition
# Não usar Azure Video Analyzer
# YOLO local = portável
```
**Economia:** $5,000 - $20,000/mês

## Resumo de Economia

### Custos Mensais

| Item | Sem Otimização | Com Otimização | Economia |
|------|----------------|----------------|----------|
| Banda | $520,000 | $5,000 | $515,000 |
| Computação | $10,000 | $500 | $9,500 |
| Armazenamento | $6,000 | $250 | $5,750 |
| Infraestrutura | $2,000 | $400 | $1,600 |
| **TOTAL** | **$538,000** | **$6,150** | **$531,850** |

### ROI (Return on Investment)

**Economia anual:** $6,382,200  
**Tempo de dev extra:** ~200 horas  
**Custo de dev:** $20,000  
**ROI:** 31,811% 🚀

## Planos de Monetização

### Basic - $49/mês
- 7 dias de gravação
- 3 usuários
- 10 câmeras
- **Margem:** 85%

### Pro - $149/mês
- 15 dias de gravação
- 5 usuários
- 50 câmeras
- Relatórios básicos
- **Margem:** 90%

### Premium - $499/mês
- 30 dias de gravação
- 10 usuários
- 200 câmeras
- Relatórios avançados
- Suporte prioritário
- **Margem:** 92%

### Enterprise - Custom
- Gravação customizada
- Usuários ilimitados
- Câmeras ilimitadas
- SLA
- Suporte 24/7
- **Margem:** 95%

## Métricas de Custo

### Por Câmera/Mês
| Plano | Custo | Receita | Lucro |
|-------|-------|---------|-------|
| Basic | $0.50 | $4.90 | $4.40 |
| Pro | $0.40 | $2.98 | $2.58 |
| Premium | $0.35 | $2.50 | $2.15 |

### Break-even
- **Clientes necessários:** 10-20
- **Tempo estimado:** 2-3 meses
- **MRR objetivo:** $10,000

## Próximas Otimizações

- [ ] WebP para thumbnails (30% menor)
- [ ] AVIF para imagens (50% menor)
- [ ] H.265 codec (50% menor que H.264)
- [ ] Edge computing (processar na câmera)
- [ ] P2P streaming (WebRTC)
- [ ] Deduplicação de vídeos similares
- [ ] AI model quantization (INT8)
- [ ] Serverless functions para picos

## Ferramentas de Monitoramento

### Custos
```bash
# AWS Cost Explorer
# Grafana dashboards
# Custom metrics
```

### Alertas
```python
# Alerta se banda > threshold
# Alerta se storage > 80%
# Alerta se CPU > 90%
```

---

**Ver também:**
- [Performance](../performance/PERFORMANCE.md)
- [Tech Stack](../TECH_STACK.md)
- [Architecture Decisions](../ARCHITECTURE_DECISIONS.md)
