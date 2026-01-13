# 🛠️ Stack Tecnológica

## Visão Geral

Stack completa do VMS com justificativas de escolha.

## Backend

### Django 4.2
**Função:** Framework web principal  
**Por quê:**
- Batteries included (ORM, Admin, Auth)
- Maturidade e estabilidade
- Grande ecossistema
- Django REST Framework

**Alternativas consideradas:**
- FastAPI (mais rápido, mas menos features)
- Flask (muito minimalista)

### PostgreSQL 15
**Função:** Banco de dados relacional  
**Por quê:**
- JSONB para dados flexíveis
- Performance excelente
- Índices avançados (GiST, GIN)
- Suporte a geolocalização (PostGIS)

**Alternativas consideradas:**
- MySQL (menos features avançadas)
- MongoDB (não relacional, menos adequado)

### Redis 7
**Função:** Cache e sessões  
**Por quê:**
- Performance extrema (in-memory)
- Pub/Sub para real-time
- TTL automático
- Estruturas de dados ricas

**Uso:**
- Cache de queries
- Sessões de usuário
- Rate limiting
- Real-time notifications

### RabbitMQ 3.13
**Função:** Message broker  
**Por quê:**
- Confiabilidade (ACK, persistência)
- Routing flexível
- Dead letter queues
- Management UI

**Uso:**
- Comunicação entre serviços
- Jobs assíncronos
- Event sourcing
- Notificações

## Frontend

### React 18
**Função:** UI library  
**Por quê:**
- Virtual DOM (performance)
- Hooks (código limpo)
- Ecossistema gigante
- Server components (futuro)

**Alternativas consideradas:**
- Vue (menos popular)
- Svelte (menos maduro)

### Vite 5
**Função:** Build tool  
**Por quê:**
- HMR instantâneo
- Build rápido (esbuild)
- Configuração simples
- ESM nativo

**Alternativas consideradas:**
- Webpack (mais lento)
- Create React App (deprecated)

### TypeScript
**Função:** Type safety  
**Por quê:**
- Catch errors em dev time
- Autocomplete melhor
- Refactoring seguro
- Documentação viva

### TailwindCSS
**Função:** CSS framework  
**Por quê:**
- Utility-first (rápido)
- Sem CSS customizado
- Tree-shaking automático
- Design system consistente

### TanStack Query (React Query)
**Função:** Data fetching  
**Por quê:**
- Cache automático
- Refetch inteligente
- Optimistic updates
- DevTools excelente

**Uso:**
```typescript
const { data: cameras } = useQuery({
  queryKey: ['cameras'],
  queryFn: cameraService.list,
})
```

## Streaming

### MediaMTX
**Função:** Servidor de streaming  
**Por quê:**
- Multi-protocolo (RTSP, HLS, WebRTC)
- Performance excelente (Go)
- On-demand streams
- API REST completa

**Alternativas consideradas:**
- Nginx-RTMP (menos features)
- Wowza (pago, caro)
- Red5 (Java, pesado)

### HLS.js
**Função:** Player HLS no browser  
**Por quê:**
- Suporte universal
- Adaptive bitrate
- Low latency mode
- Bem mantido

**Alternativas consideradas:**
- Video.js (mais pesado)
- Plyr (menos features)

### FFmpeg
**Função:** Processamento de vídeo  
**Por quê:**
- Swiss army knife de vídeo
- Performance nativa (C)
- Todos os codecs
- CLI poderoso

**Uso:**
- Transcodificação
- Thumbnail generation
- Recording
- Clipping

## IA/ML

### YOLOv8
**Função:** Object detection  
**Por quê:**
- State-of-the-art accuracy
- Real-time performance
- Modelos otimizados (nano)
- Fácil de usar (Ultralytics)

**Modelos:**
- YOLOv8n: Nano (mais rápido)
- YOLOv8s: Small
- YOLOv8m: Medium

### Fast-Plate-OCR
**Função:** Leitura de placas  
**Por quê:**
- Otimizado para placas
- CPU-friendly
- Alta precisão
- Open source

### PyTorch
**Função:** ML framework  
**Por quê:**
- Padrão da indústria
- Pythonic
- Dynamic graphs
- Grande comunidade

**Configuração:**
```python
# CPU-only para reduzir custos
torch.set_num_threads(4)
device = 'cpu'
```

## Infraestrutura

### Docker
**Função:** Containerização  
**Por quê:**
- Isolamento
- Reprodutibilidade
- Fácil deploy
- Orquestração

### Docker Compose
**Função:** Multi-container orchestration  
**Por quê:**
- Dev environment simples
- Networking automático
- Volume management
- Service dependencies

**Estrutura:**
```yaml
services:
  - backend (Django)
  - frontend (React)
  - mediamtx (Streaming)
  - lpr_detection (IA)
  - postgres
  - redis
  - rabbitmq
```

### Prometheus
**Função:** Monitoring  
**Por quê:**
- Time-series DB
- Pull-based
- Alerting
- Grafana integration

**Métricas:**
- CPU/Memory usage
- Request latency
- Error rates
- Custom metrics

## Protocolos

### RTSP (Real Time Streaming Protocol)
**Uso:** Entrada de câmeras  
**Por quê:**
- Padrão de câmeras IP
- Low latency
- Reliable

### HLS (HTTP Live Streaming)
**Uso:** Saída para web  
**Por quê:**
- HTTP-based (firewall-friendly)
- Adaptive bitrate
- Browser support
- CDN-friendly

### WebRTC (futuro)
**Uso:** Ultra-low latency  
**Por quê:**
- P2P capable
- Sub-second latency
- Browser native

## Linguagens

### Python 3.11
**Uso:** Backend, IA  
**Por quê:**
- Produtividade
- ML ecosystem
- Django
- Type hints

### TypeScript 5
**Uso:** Frontend  
**Por quê:**
- Type safety
- Modern features
- Tooling

### Go (MediaMTX)
**Uso:** Streaming server  
**Por quê:**
- Performance
- Concurrency
- Single binary

## Bibliotecas Principais

### Backend
```python
Django==4.2
djangorestframework==3.14
psycopg2-binary==2.9
redis==5.0
celery==5.3
ultralytics==8.0  # YOLO
opencv-python==4.8
```

### Frontend
```json
{
  "react": "^18.2.0",
  "vite": "^5.0.0",
  "@tanstack/react-query": "^5.0.0",
  "hls.js": "^1.4.0",
  "tailwindcss": "^3.4.0",
  "lucide-react": "^0.300.0"
}
```

## Decisões de Arquitetura

### Por que não usar AWS Rekognition?
- **Custo:** $1-5 por 1000 imagens
- **Latência:** API calls lentas
- **Vendor lock-in:** Dependência AWS
- **Solução:** YOLO local (CPU)

### Por que CPU-only para IA?
- **Custo:** GPU cloud = $500-2000/mês
- **Performance:** YOLOv8n roda bem em CPU
- **Escalabilidade:** Horizontal scaling
- **Solução:** Otimizações + frame skipping

### Por que HLS e não WebRTC?
- **Simplicidade:** HLS é HTTP
- **Compatibilidade:** Funciona em todos browsers
- **CDN:** Fácil de cachear
- **Futuro:** Adicionar WebRTC depois

### Por que Django e não FastAPI?
- **Admin panel:** Grátis e poderoso
- **ORM:** Migrations automáticas
- **Auth:** Sistema completo
- **Maturidade:** Mais estável

## Custos Estimados

### Cloud (AWS/Azure)
| Componente | Custo/mês |
|------------|-----------|
| EC2 (backend) | $50-100 |
| RDS (postgres) | $30-80 |
| S3 (storage) | $20-200 |
| Bandwidth | $50-500 |
| **Total** | **$150-880** |

### Self-hosted
| Componente | Custo/mês |
|------------|-----------|
| VPS (8GB RAM) | $40-80 |
| Storage (1TB) | $10-20 |
| Bandwidth | $0-50 |
| **Total** | **$50-150** |

---

**Ver também:**
- [Architecture Decisions](./ARCHITECTURE_DECISIONS.md)
- [Cost Optimization](./cost-optimization/)
- [Performance](./performance/)
