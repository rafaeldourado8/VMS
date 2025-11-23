# 🎥 Sistema de Vigilância Inteligente

<div align="center">

![Vigilância](https://img.shields.io/badge/Status-Em%20Desenvolvimento-yellow)
![License](https://img.shields.io/badge/License-MIT-blue)
![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)
![Django](https://img.shields.io/badge/Django-5.0-green?logo=django)
![React](https://img.shields.io/badge/React-18-blue?logo=react)
![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)

**Plataforma completa de videovigilância com detecção de IA, streaming em tempo real e analytics avançados**

[📸 Funcionalidades](#-principais-características) • [🏗️ Arquitetura](#️-arquitetura) • [🚀 Instalação](#-instalação) • [📚 Documentação](#-documentação) • [🤝 Contribuir](#-contribuir)

</div>

---

## 📋 Sobre o Projeto

Sistema moderno e escalável de vigilância por vídeo que combina streaming de baixa latência, detecção inteligente por IA e análise de dados em tempo real. Desenvolvido com tecnologias de ponta para garantir performance, confiabilidade e facilidade de uso.

### 🎯 Principais Características

| Característica | Descrição |
|---------------|-----------|
| 🎬 **Streaming em Tempo Real** | Visualização de múltiplas câmaras com latência inferior a 500ms (WebRTC) |
| 🤖 **Detecção por IA** | Reconhecimento automático de pessoas, veículos e objetos com alta precisão |
| 📊 **Analytics Avançados** | Dashboard interativo com métricas, gráficos e relatórios exportáveis |
| 🔐 **Segurança Robusta** | Autenticação JWT, permissões granulares e auditoria completa |
| ⚡ **Alta Performance** | Processamento assíncrono, cache inteligente e otimização de queries |
| 📱 **Responsivo** | Interface adaptável para desktop, tablet e mobile |
| 🐳 **Docker Ready** | Deploy simplificado com docker-compose |
| 🔄 **Escalável** | Arquitetura preparada para crescimento horizontal |

---

## 🏗️ Arquitetura

### Visão Geral do Sistema

```mermaid
graph TB
    subgraph "Cliente"
        Browser[🌐 Navegador Web]
    end

    subgraph "Proxy Layer"
        Nginx[⚙️ Nginx<br/>Reverse Proxy]
    end

    subgraph "Application Layer"
        Frontend[⚛️ React Frontend<br/>TypeScript + Vite]
        Backend[🐍 Django API<br/>REST Framework]
        Workers[👷 Celery Workers<br/>Processamento Assíncrono]
    end

    subgraph "Streaming Layer"
        MediaMTX[📹 MediaMTX<br/>RTSP/WebRTC/HLS]
        FFmpeg[🎬 FFmpeg<br/>Transcodificação]
    end

    subgraph "Data Layer"
        Redis[(🗄️ Redis<br/>Cache & Queue)]
        Postgres[(🐘 PostgreSQL<br/>Database)]
        RabbitMQ[🐰 RabbitMQ<br/>Message Broker]
    end

    subgraph "External"
        Cameras[📷 Câmaras IP<br/>RTSP Streams]
        AIService[🧠 Serviço IA<br/>Detecção de Objetos]
    end

    Browser -->|HTTPS| Nginx
    Nginx --> Frontend
    Nginx --> Backend
    Nginx --> MediaMTX
    
    Frontend --> Backend
    Backend --> Redis
    Backend --> Postgres
    Backend --> RabbitMQ
    
    RabbitMQ --> Workers
    Workers --> Redis
    Workers --> Postgres
    
    Cameras --> MediaMTX
    MediaMTX --> FFmpeg
    FFmpeg --> MediaMTX
    Backend --> MediaMTX
    AIService --> Backend
    
    style Browser fill:#e1f5ff
    style Nginx fill:#ff9999
    style Frontend fill:#ffb366
    style Backend fill:#90ee90
    style Workers fill:#ffcc99
    style Postgres fill:#9999ff
    style Redis fill:#ff6666
    style MediaMTX fill:#ff99ff
    style FFmpeg fill:#99ffff
```

### Fluxo de Processamento de Vídeo

```mermaid
sequenceDiagram
    participant CAM as 📷 Câmara IP
    participant MTX as MediaMTX
    participant FF as FFmpeg
    participant BE as Backend
    participant AI as Serviço IA
    participant FE as Frontend
    
    Note over CAM,FE: Streaming e Detecção em Tempo Real
    
    CAM->>MTX: RTSP Stream<br/>(H.264/H.265)
    MTX->>MTX: Recebe stream<br/>porta :8554
    
    par Streaming para Cliente
        MTX->>FF: Transcodifica se necessário<br/>(baixar bitrate/resolução)
        FF-->>MTX: Stream otimizado
        MTX->>FE: WebRTC Stream<br/>(latência <500ms)
        MTX->>FE: HLS Stream<br/>(fallback, 6-20s)
    and Processamento IA
        MTX->>FF: Extrai frames<br/>(1 frame/segundo)
        FF->>AI: POST /detect<br/>Frame JPEG
        AI->>AI: Detecta objetos<br/>(YOLO/SSD)
        AI-->>BE: POST /api/deteccoes/ingest/<br/>{tipo, confiança, bbox}
        BE->>BE: Valida e processa
        BE->>Postgres: Salva detecção
        BE->>Redis: Cache + alertas
        BE->>FE: WebSocket push<br/>Notificação real-time
    end
    
    FE-->>FE: Atualiza UI<br/>Stream + Alertas
```

<details>
<summary>🎯 <b>Navegação Intuitiva - Controles Especiais</b></summary>

### Joystick de Navegação (Grid de Câmaras)
```
         ▲ Cima
         │
    ◄────┼────► Direita
         │
         ▼ Baixo
    Esquerda
```

- **Setas do teclado**: Navega entre câmaras no grid
- **Enter**: Maximiza câmara selecionada
- **Esc**: Volta ao grid completo
- **Espaço**: Pausa/Resume stream
- **F**: Fullscreen
- **M**: Mute/Unmute
- **1-9**: Acesso rápido às primeiras 9 câmaras

### Controles PTZ (Pan-Tilt-Zoom)
Para câmaras compatíveis:
- **Arrastar mouse**: Pan & Tilt
- **Scroll wheel**: Zoom in/out
- **Clique duplo**: Auto-focus no ponto
- **Ctrl + Setas**: Movimento preciso

</details>

---

## 🔧 Stack Tecnológica

### Backend
| Tecnologia | Versão | Uso |
|-----------|--------|-----|
| **Django** | 5.0 | Framework web principal |
| **Django REST Framework** | 3.14+ | API RESTful |
| **Simple JWT** | Latest | Autenticação JWT |
| **Gunicorn** | 21+ | Servidor WSGI |
| **Celery** | 5.3+ | Tasks assíncronas |
| **RabbitMQ** | 3.12+ | Message broker |
| **Redis** | 7.0+ | Cache & results backend |
| **PostgreSQL** | 15+ | Database principal |

### Frontend
| Tecnologia | Versão | Uso |
|-----------|--------|-----|
| **React** | 18 | UI framework |
| **TypeScript** | 5+ | Type safety |
| **Vite** | 5+ | Build tool |
| **TanStack Query** | 5+ | Data fetching |
| **Zustand** | 4+ | State management |
| **Tailwind CSS** | 3+ | Styling |
| **shadcn/ui** | Latest | Componentes UI |
| **Recharts** | 2+ | Gráficos |
| **Axios** | 1+ | HTTP client |

### Streaming & Media
| Tecnologia | Versão | Uso |
|-----------|--------|-----|
| **MediaMTX** | Latest | Servidor RTSP/WebRTC/HLS |
| **FFmpeg** | 6.0+ | Transcodificação de vídeo |
| **WebRTC** | - | Streaming baixa latência |
| **HLS** | - | Streaming fallback |

### Infrastructure
| Tecnologia | Versão | Uso |
|-----------|--------|-----|
| **Docker** | 20.10+ | Containerização |
| **Docker Compose** | 2.0+ | Orquestração |
| **Nginx** | 1.25+ | Reverse proxy |
| **PgBouncer** | 1.21+ | Connection pooling |

---

## ✨ Funcionalidades Detalhadas

### 👤 Gestão de Utilizadores
- ✅ Sistema completo de autenticação (login, logout, refresh token)
- ✅ Perfis de utilizador com permissões granulares
- ✅ Gestão de grupos e políticas de acesso
- ✅ Auditoria de ações (logs de atividade)
- ✅ Recuperação de senha por email
- ✅ Sessões simultâneas em múltiplos dispositivos

### 📹 Gestão de Câmaras
- ✅ Adicionar/editar/remover câmaras IP (RTSP)
- ✅ Visualização em tempo real (WebRTC/HLS)
- ✅ Grid de múltiplas câmaras simultâneas (4, 9, 16, 25)
- ✅ Controles de PTZ (Pan-Tilt-Zoom) quando suportado
- ✅ Health check automático com reconexão inteligente
- ✅ Thumbnails e preview de streams
- ✅ Configurações individuais (FPS, resolução, bitrate)
- ✅ Agendamento de gravações
- ✅ Zonas de privacidade (mascaramento)

### 🤖 Detecção e Alertas
- ✅ Ingestão de alto volume (>1000 detecções/segundo)
- ✅ Classificação automática (pessoas, veículos, animais, objetos)
- ✅ Zonas de interesse personalizáveis
- ✅ Filtros de confiança e cooldown entre alertas
- ✅ Notificações em tempo real (WebSocket)
- ✅ Histórico completo com busca avançada
- ✅ Exportação de frames e vídeos
- ✅ Integração com webhooks para sistemas externos

### 📊 Analytics e Relatórios
- ✅ Dashboard em tempo real com métricas chave
- ✅ Gráficos interativos (detecções por hora, top câmaras)
- ✅ Heatmaps de atividade
- ✅ Estatísticas agregadas (diário, semanal, mensal)
- ✅ Exportação de relatórios (PDF, CSV, Excel)
- ✅ Comparação de períodos
- ✅ Alertas por threshold
- ✅ Tendências e predições

---

## 🚀 Instalação

### Pré-requisitos
```bash
# Versões mínimas
Docker 20.10+
Docker Compose 2.0+
Git 2.30+

# Recursos recomendados
CPU: 4+ cores
RAM: 8GB+
Storage: 50GB+ (SSD recomendado)
```

### 🎬 Quick Start

#### 1️⃣ Clone o Repositório
```bash
git clone https://github.com/rafaeldourado8/vigilancia-system.git
cd vigilancia-system
```

#### 2️⃣ Configuração Rápida
```bash
# Copie o arquivo de ambiente
cp .env.example .env

# Edite as variáveis (use nano, vim ou seu editor favorito)
nano .env
```

**Variáveis essenciais:**
```bash
# Django
SECRET_KEY=sua-chave-secreta-super-segura-aqui-min-50-chars
DEBUG=False
ALLOWED_HOSTS=seu-dominio.com,localhost,127.0.0.1

# Database
POSTGRES_DB=vigilancia_db
POSTGRES_USER=vigilancia_user
POSTGRES_PASSWORD=SenhaForte123!@#

# Redis
REDIS_PASSWORD=RedisSecure456!@#

# RabbitMQ
RABBITMQ_DEFAULT_USER=admin
RABBITMQ_DEFAULT_PASS=RabbitMQ789!@#

# MediaMTX
MEDIAMTX_API_URL=http://mediamtx:9997
MEDIAMTX_RTSP_PORT=8554
MEDIAMTX_HLS_PORT=8888
MEDIAMTX_WEBRTC_PORT=8889

# AI Service (opcional)
AI_SERVICE_URL=http://seu-servico-ia:8080
AI_SERVICE_TOKEN=token-de-autenticacao-aqui
AI_SERVICE_ENABLED=True

# Email (opcional, para recuperação de senha)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-app
```

#### 3️⃣ Inicie o Sistema
```bash
# Build e inicie todos os containers
docker-compose up -d --build

# Aguarde ~30 segundos para inicialização completa
# Acompanhe os logs
docker-compose logs -f
```

#### 4️⃣ Configuração Inicial
```bash
# Execute as migrações do banco
docker-compose exec backend python manage.py migrate

# Crie um superusuário
docker-compose exec backend python manage.py createsuperuser
# Siga as instruções interativas

# (Opcional) Carregue dados de exemplo
docker-compose exec backend python manage.py loaddata initial_data.json
```

#### 5️⃣ Acesse a Aplicação
```
✅ Frontend: http://localhost
✅ API: http://localhost/api/
✅ Admin Django: http://localhost/admin/
✅ Documentação API: http://localhost/api/docs/
✅ MediaMTX API: http://localhost:9997
```

### 🔍 Verificação de Saúde
```bash
# Verifique status de todos os serviços
docker-compose ps

# Teste a API
curl http://localhost/api/health/

# Verifique logs de um serviço específico
docker-compose logs backend
docker-compose logs mediamtx
docker-compose logs celery-worker
```

---

## 🎬 Desenvolvimento Local

### Backend
```bash
cd backend

# Crie ambiente virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instale dependências
pip install -r requirements/dev.txt

# Configure variáveis de ambiente
cp .env.example .env
# Edite .env com configurações de desenvolvimento

# Execute migrações
python manage.py migrate

# Crie superusuário
python manage.py createsuperuser

# Inicie servidor
python manage.py runserver
```

### Frontend
```bash
cd frontend

# Instale dependências
npm install

# Configure variáveis de ambiente
cp .env.example .env.local
# Edite .env.local

# Inicie servidor de desenvolvimento
npm run dev

# Build para produção
npm run build

# Preview do build
npm run preview
```

### Serviços Auxiliares (Docker)
```bash
# Apenas serviços de infraestrutura
docker-compose up -d postgres redis rabbitmq mediamtx

# Backend e frontend local se conectam a esses serviços
```

---

## 📚 Documentação

### Estrutura do Projeto
```
vigilancia-system/
├── 📂 backend/                    # Django Backend
│   ├── 📂 apps/                   # Django Apps
│   │   ├── 📂 usuarios/          # Autenticação e utilizadores
│   │   ├── 📂 cameras/           # Gestão de câmaras
│   │   ├── 📂 deteccoes/         # Detecções de IA
│   │   ├── 📂 analytics/         # Analytics e reports
│   │   └── 📂 dashboard/         # Dashboard real-time
│   ├── 📂 config/                # Configurações Django
│   ├── 📂 core/                  # Utilitários compartilhados
│   └── 📂 streaming_integration/ # Integração MediaMTX
│
├── 📂 frontend/                   # React Frontend
│   ├── 📂 src/
│   │   ├── 📂 components/        # Componentes React
│   │   ├── 📂 pages/            # Páginas/Rotas
│   │   ├── 📂 hooks/            # Custom Hooks
│   │   ├── 📂 services/         # API Services
│   │   ├── 📂 store/            # Estado Global (Zustand)
│   │   └── 📂 types/            # TypeScript Types
│   └── 📂 public/
│
├── 📂 docker/                     # Dockerfiles e configs
│   ├── 📂 backend/
│   ├── 📂 frontend/
│   ├── 📂 nginx/
│   └── 📂 mediamtx/
│
├── 📂 database/                   # Scripts SQL
│   ├── 📂 migrations/
│   └── 📂 seeds/
│
├── 📂 docs/                       # Documentação adicional
│   ├── 📄 API.md
│   ├── 📄 DEPLOYMENT.md
│   ├── 📄 ARCHITECTURE.md
│   └── 📄 USER_GUIDE.md
│
├── 📄 docker-compose.yml         # Orquestração Docker
├── 📄 .env.example               # Exemplo de variáveis
└── 📄 README.md                  # Este arquivo
```

### API Endpoints Principais

#### 🔐 Autenticação
```http
POST   /api/auth/login/          # Login (retorna access + refresh token)
POST   /api/auth/refresh/        # Refresh access token
POST   /api/auth/logout/         # Logout (blacklist do token)
GET    /api/auth/me/             # Dados do utilizador atual
PUT    /api/auth/me/             # Atualizar perfil
POST   /api/auth/password/change/ # Alterar senha
POST   /api/auth/password/reset/  # Recuperação de senha
```

#### 📹 Câmaras
```http
GET    /api/cameras/             # Lista câmaras (com filtros)
POST   /api/cameras/             # Criar câmara
GET    /api/cameras/{id}/        # Detalhes da câmara
PUT    /api/cameras/{id}/        # Atualizar câmara
PATCH  /api/cameras/{id}/        # Atualização parcial
DELETE /api/cameras/{id}/        # Remover câmara
GET    /api/cameras/{id}/stream/ # Informações do stream
GET    /api/cameras/{id}/health/ # Health check
POST   /api/cameras/{id}/ptz/    # Controle PTZ
GET    /api/cameras/{id}/snapshot/ # Captura frame atual
```

#### 🤖 Detecções
```http
GET    /api/deteccoes/           # Lista detecções (com filtros avançados)
POST   /api/deteccoes/ingest/    # Ingerir detecção (chamada da IA)
GET    /api/deteccoes/{id}/      # Detalhes da detecção
GET    /api/deteccoes/recentes/  # Detecções recentes (últimas 100)
GET    /api/deteccoes/stats/     # Estatísticas gerais
POST   /api/deteccoes/bulk/      # Ingestão em massa
DELETE /api/deteccoes/cleanup/   # Limpeza de dados antigos
```

#### 📊 Analytics
```http
GET    /api/analytics/dashboard/       # Stats do dashboard
GET    /api/analytics/deteccoes/       # Série temporal de detecções
GET    /api/analytics/cameras/top/     # Top câmaras por métrica
GET    /api/analytics/heatmap/         # Dados para heatmap
POST   /api/analytics/reports/export/  # Exportar relatório
GET    /api/analytics/reports/{id}/    # Status do relatório
GET    /api/analytics/trends/          # Análise de tendências
```

### 📖 Documentação Completa da API
Acesse a documentação interativa em: **http://localhost/api/docs/**
- Interface Swagger UI
- Especificação OpenAPI 3.0
- Testes interativos
- Exemplos de requests/responses

---

## 🧪 Testes

### Backend
```bash
# Todos os testes
docker-compose exec backend python manage.py test

# Testes de uma app específica
docker-compose exec backend python manage.py test apps.cameras

# Com coverage
docker-compose exec backend pytest --cov=apps --cov-report=html
# Relatório em: backend/htmlcov/index.html

# Testes de integração
docker-compose exec backend pytest tests/integration/

# Testes de performance
docker-compose exec backend pytest tests/performance/ --benchmark
```

### Frontend
```bash
cd frontend

# Testes unitários
npm run test

# Testes com coverage
npm run test:coverage

# Testes E2E (Playwright)
npm run test:e2e

# Testes E2E em modo UI
npm run test:e2e:ui

# Testes de um componente específico
npm run test -- CameraGrid
```

### Testes de Carga
```bash
# Usando k6
k6 run tests/load/streaming_test.js

# Usando locust
locust -f tests/load/api_load.py --host=http://localhost
```

---

## 🔧 Configuração de Câmaras

### Adicionar Câmara RTSP

#### Via Interface Web:
1. Aceda a **"Câmaras" → "Adicionar Câmara"**
2. Preencha os campos:
   - **Nome**: Identificação da câmara
   - **URL RTSP**: Endereço do stream
   - **Localização**: Local físico
   - **Ativa**: Marque para ativar imediatamente

**Exemplo de URL RTSP:**
```
rtsp://admin:senha123@192.168.1.100:554/stream1
```

#### Via API:
```bash
curl -X POST http://localhost/api/cameras/ \
  -H "Authorization: Bearer SEU_TOKEN_JWT" \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Câmara Entrada Principal",
    "rtsp_url": "rtsp://admin:senha@192.168.1.100:554/stream1",
    "localizacao": "Entrada Principal",
    "ativa": true,
    "fps": 25,
    "resolucao": "1920x1080",
    "enable_ptz": true,
    "enable_audio": false
  }'
```

### Formatos RTSP por Fabricante

| Fabricante | Formato URL | Porta Padrão |
|-----------|-------------|--------------|
| **Hikvision** | `rtsp://user:pass@ip:554/Streaming/Channels/101` | 554 |
| **Dahua** | `rtsp://user:pass@ip:554/cam/realmonitor?channel=1&subtype=0` | 554 |
| **Axis** | `rtsp://user:pass@ip:554/axis-media/media.amp` | 554 |
| **Foscam** | `rtsp://user:pass@ip:554/videoMain` | 88 |
| **TP-Link** | `rtsp://user:pass@ip:554/stream1` | 554 |
| **Generic** | `rtsp://user:pass@ip:554/stream1` | 554 |

### Teste Manual de Câmara
```bash
# Teste com FFmpeg
ffplay rtsp://admin:senha@192.168.1.100:554/stream1

# Teste com VLC
vlc rtsp://admin:senha@192.168.1.100:554/stream1

# Verificar codec e resolução
ffprobe -v error -select_streams v:0 \
  -show_entries stream=codec_name,width,height \
  -of default=noprint_wrappers=1 \
  rtsp://admin:senha@192.168.1.100:554/stream1
```

---

## 🔐 Segurança

### Boas Práticas Implementadas
- ✅ Tokens JWT com expiração (5min access, 7d refresh)
- ✅ Passwords hasheadas com PBKDF2 (100k iterações)
- ✅ Rate limiting em endpoints críticos (100 req/min)
- ✅ CORS configurado adequadamente
- ✅ HTTPS obrigatório em produção
- ✅ SQL injection prevention (ORM do Django)
- ✅ XSS protection (React + DRF sanitization)
- ✅ CSRF tokens para forms
- ✅ Logs de auditoria completos
- ✅ Validação de inputs (backend + frontend)
- ✅ Sanitização de URLs RTSP
- ✅ Secrets em variáveis de ambiente

### 🔒 Checklist de Segurança para Produção

```bash
# 1. Senhas fortes (min. 16 caracteres, letras+números+símbolos)
SECRET_KEY=... # 50+ caracteres aleatórios
POSTGRES_PASSWORD=...
REDIS_PASSWORD=...
RABBITMQ_DEFAULT_PASS=...

# 2. Desative DEBUG
DEBUG=False

# 3. Configure ALLOWED_HOSTS
ALLOWED_HOSTS=seu-dominio.com,api.seu-dominio.com

# 4. HTTPS obrigatório
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# 5. Configure firewall
sudo ufw allow 80/tcp   # HTTP (redireciona para HTTPS)
sudo ufw allow 443/tcp  # HTTPS
sudo ufw deny 8000/tcp  # Bloqueia acesso direto ao Django
sudo ufw deny 5432/tcp  # Bloqueia acesso externo ao Postgres

# 6. Certificado SSL (Let's Encrypt)
sudo certbot --nginx -d seu-dominio.com

# 7. Backup automático
# Configure cron para backup diário
0 3 * * * /app/scripts/backup_db.sh

# 8. Monitore logs
docker-compose logs -f | grep -i "error\|warning\|unauthorized"

# 9. Atualizações de segurança
pip list --outdated
npm outdated

# 10. Auditoria de dependências
pip-audit
npm audit
```

---

## 📈 Performance

### Métricas de Referência
| Métrica | Valor | Condições |
|---------|-------|-----------|
| **API Response Time** | <100ms | Média, com cache |
| **WebRTC Latency** | 100-500ms | Rede local |
| **HLS Latency** | 6-20s | Fallback |
| **Detecções/segundo** | >1000 | 4 workers Celery |
| **Câmaras simultâneas** | 50+ | Por servidor |
| **Concurrent users** | 100+ | Com load balancer |
| **Database queries** | <50ms | 95th percentile |
| **Cache hit rate** | >80% | Redis |

### Otimizações Implementadas

#### Backend
- ✅ Connection pooling (PgBouncer: 100 connections)
- ✅ Query optimization com índices estratégicos
- ✅ Cache em Redis (TTL inteligente: 30s-5min)
- ✅ Processamento assíncrono (Celery: 4 workers)
- ✅ Static files via Whitenoise (zero disk I/O)
- ✅ Serialização otimizada (select_related, prefetch_related)
- ✅ Paginação em todas listagens (page_size: 50)
- ✅ Rate limiting inteligente

#### Frontend
- ✅ Lazy loading de componentes (React.lazy)
- ✅ Code splitting automático (Vite)
- ✅ Debounce em inputs de busca (300ms)
- ✅ Virtual scrolling em listas longas
- ✅ Memoization de componentes pesados
- ✅ Image lazy loading nativa
- ✅ Service worker para cache (PWA ready)

#### Infraestrutura
- ✅ Gzip compression (Nginx: nivel 6)
- ✅ Static assets caching (1 ano)
- ✅ HTTP/2 enabled
- ✅ CDN ready (CloudFront/Cloudflare)
- ✅ Health checks automáticos (cada 30s)

### Monitoramento
```bash
# Prometheus + Grafana (opcional)
docker-compose -f docker-compose.monitoring.yml up -d

# Métricas disponíveis em:
http://localhost:9090  # Prometheus
http://localhost:3000  # Grafana (admin/admin)

# Dashboards pré-configurados:
- Django metrics
- PostgreSQL performance
- Redis stats
- Celery tasks
- MediaMTX streams
```

---

## 🐛 Troubleshooting (Continuação)

### ❌ Problemas Comuns

#### 1. Câmara não conecta

```bash
# Teste a URL RTSP diretamente com FFmpeg
ffplay rtsp://admin:senha@192.168.1.100:554/stream1

# Verifique logs do MediaMTX
docker-compose logs mediamtx | grep -i error

# Teste conectividade de rede
ping 192.168.1.100

# Verifique firewall da câmara (porta 554 deve estar aberta)

# Teste autenticação
curl -v rtsp://admin:senha@192.168.1.100:554/

# Possíveis soluções:
# - Verifique credenciais (user/password)
# - Confirme URL RTSP correta (consulte manual da câmara)
# - Verifique se câmara está na mesma rede
# - Desative firewall temporariamente para teste
# - Alguns modelos requerem ativar RTSP nas configurações
```

#### 2. Alto uso de CPU/RAM

```bash
# Identifique container problemático
docker stats

# Se for FFmpeg:
# - Reduza resolução nas configurações da câmara
# - Reduza FPS (de 25 para 15)
# - Use codec H.264 em vez de H.265
# - Desative transcodificação se possível

# Se for Celery:
# - Reduza número de workers
# - Aumente CELERY_TASK_RATE_LIMIT

# Se for PostgreSQL:
# - Execute VACUUM ANALYZE
docker-compose exec postgres psql -U vigilancia_user -d vigilancia_db -c "VACUUM ANALYZE;"
# - Verifique queries lentas no log
```

#### 3. Erros de autenticação JWT

```bash
# Token expirado - faça refresh
curl -X POST http://localhost/api/auth/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "SEU_REFRESH_TOKEN"}'

# Se refresh também falhou, faça login novamente
# Verifique se SECRET_KEY não mudou (invalida todos tokens)

# Limpe tokens blacklistados antigos (>7 dias)
docker-compose exec backend python manage.py flushexpiredtokens
```

#### 4. Detecções não aparecem

```bash
# Verifique se Celery está rodando
docker-compose ps celery-worker

# Verifique fila do RabbitMQ
docker-compose exec rabbitmq rabbitmqctl list_queues

# Teste ingestão manual
curl -X POST http://localhost/api/deteccoes/ingest/ \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "camera_id": 1,
    "tipo_objeto": "pessoa",
    "confianca": 0.95,
    "bbox": {"x": 100, "y": 100, "w": 200, "h": 300}
  }'

# Verifique logs do Celery
docker-compose logs celery-worker | tail -50
```

#### 5. Banco de dados lento

```bash
# Verifique queries lentas (>1s)
docker-compose exec postgres psql -U vigilancia_user -d vigilancia_db -c "
  SELECT query, calls, total_time, mean_time 
  FROM pg_stat_statements 
  ORDER BY mean_time DESC 
  LIMIT 10;
"

# Reconstrua índices
docker-compose exec backend python manage.py sqlflush
docker-compose exec backend python manage.py migrate --run-syncdb

# Limpe dados antigos (>30 dias)
docker-compose exec backend python manage.py shell -c "
from apps.deteccoes.models import Deteccao
from datetime import datetime, timedelta
threshold = datetime.now() - timedelta(days=30)
Deteccao.objects.filter(timestamp__lt=threshold).delete()
"
```

#### 6. Websocket não conecta

```bash
# Verifique Nginx config para websocket
cat docker/nginx/nginx.conf | grep -A5 "websocket"

# Teste conexão websocket manualmente
wscat -c ws://localhost/ws/dashboard/

# Verifique CORS e ALLOWED_HOSTS
# Frontend e backend devem estar no mesmo domínio ou CORS configurado

# Possíveis soluções:
# - Adicione domínio frontend em ALLOWED_HOSTS
# - Configure CORS_ALLOWED_ORIGINS corretamente
# - Verifique se Redis está acessível
```

#### 7. Frontend não carrega

```bash
# Verifique build do frontend
docker-compose logs frontend

# Reconstrua assets
docker-compose exec frontend npm run build

# Verifique permissões
docker-compose exec frontend ls -la /app/dist

# Limpe cache do navegador (Ctrl+F5)

# Verifique console do navegador para erros
# Inspecione Network tab para requisições falhadas
```

#### 8. Migrações do banco falham

```bash
# Liste migrações aplicadas
docker-compose exec backend python manage.py showmigrations

# Faça fake de migração problemática (último recurso!)
docker-compose exec backend python manage.py migrate --fake app_name migration_name

# Reverta migrações
docker-compose exec backend python manage.py migrate app_name zero

# Reaplique tudo
docker-compose exec backend python manage.py migrate

# Se tudo falhar, recrie banco (PERDE DADOS!)
docker-compose down -v
docker-compose up -d
docker-compose exec backend python manage.py migrate
```

---

## 📦 Deploy em Produção

### Opções de Hosting

#### 1️⃣ VPS/Dedicated Server (AWS EC2, DigitalOcean, Hetzner)

**Requisitos mínimos:**
- 4 vCPUs
- 8GB RAM
- 100GB SSD
- Ubuntu 22.04 LTS

**Setup:**

```bash
# Atualize sistema
sudo apt update && sudo apt upgrade -y

# Instale Docker e Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Clone o projeto
git clone https://github.com/rafaeldourado8/vigilancia-system.git
cd vigilancia-system

# Configure variáveis de produção
cp .env.example .env
nano .env  # Configure TODAS as variáveis

# Inicie serviços
docker-compose -f docker-compose.prod.yml up -d

# Configure SSL com Let's Encrypt
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d seu-dominio.com

# Configure firewall
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# Setup backup automático
sudo crontab -e
# Adicione: 0 3 * * * /app/scripts/backup.sh
```

#### 2️⃣ Kubernetes (AWS EKS, GKE, AKS)

```bash
# Helm charts disponíveis em /k8s
helm install vigilancia ./k8s/helm \
  --namespace vigilancia \
  --create-namespace \
  --values values.prod.yaml

# Configure autoscaling
kubectl autoscale deployment backend --cpu-percent=70 --min=2 --max=10
```

#### 3️⃣ Cloud Platform as a Service

- **Backend**: Railway, Render, Fly.io
- **Database**: AWS RDS, DigitalOcean Managed Postgres
- **Cache**: AWS ElastiCache, Redis Cloud
- **Storage**: AWS S3, DigitalOcean Spaces
- **CDN**: CloudFront, Cloudflare

---

## 🔄 Manutenção

### Backup Automático

```bash
#!/bin/bash
# /app/scripts/backup.sh

BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup do banco
docker-compose exec -T postgres pg_dump -U vigilancia_user vigilancia_db | gzip > "$BACKUP_DIR/db_$DATE.sql.gz"

# Backup dos media files
tar -czf "$BACKUP_DIR/media_$DATE.tar.gz" -C /var/lib/docker/volumes/vigilancia_media_files/_data .

# Remove backups >7 dias
find $BACKUP_DIR -name "*.gz" -mtime +7 -delete

echo "Backup concluído: $DATE"
```

### Atualização do Sistema

```bash
# 1. Backup
./scripts/backup.sh

# 2. Pull da última versão
git pull origin main

# 3. Rebuild containers
docker-compose down
docker-compose pull
docker-compose up -d --build

# 4. Migrações
docker-compose exec backend python manage.py migrate

# 5. Collect static
docker-compose exec backend python manage.py collectstatic --noinput

# 6. Verificação
docker-compose ps
curl http://localhost/api/health/
```

### Limpeza de Dados

```bash
# Limpa detecções antigas (>30 dias)
docker-compose exec backend python manage.py shell -c "
from apps.deteccoes.models import Deteccao
from django.utils import timezone
from datetime import timedelta
threshold = timezone.now() - timedelta(days=30)
deleted = Deteccao.objects.filter(timestamp__lt=threshold).delete()
print(f'Deletadas {deleted[0]} detecções antigas')
"

# Limpa logs antigos
docker-compose exec backend find /app/logs -name "*.log" -mtime +7 -delete

# Limpa imagens Docker não utilizadas
docker system prune -af --volumes
```

---

## 🤝 Contribuir

Contribuições são muito bem-vindas! Este projeto segue o padrão de [Conventional Commits](https://www.conventionalcommits.org/).

### Como Contribuir

1. **Fork** o projeto
2. **Clone** seu fork
   ```bash
   git clone https://github.com/seu-usuario/vigilancia-system.git
   cd vigilancia-system
   ```
3. **Crie uma branch** para sua feature
   ```bash
   git checkout -b feature/minha-nova-feature
   ```
4. **Faça suas alterações** e commit
   ```bash
   git commit -m "feat: adiciona suporte para câmaras PTZ avançadas"
   ```
5. **Push** para seu fork
   ```bash
   git push origin feature/minha-nova-feature
   ```
6. Abra um **Pull Request** detalhado

### Padrão de Commits

```
feat: nova funcionalidade
fix: correção de bug
docs: documentação
style: formatação, ponto e vírgula, etc
refactor: refatoração de código
test: adição de testes
chore: atualização de dependências, configs
```

### Código de Conduta

- Seja respeitoso e inclusivo
- Aceite críticas construtivas
- Foque no que é melhor para a comunidade
- Tenha empatia com outros membros

---

## 🧪 Testes e Quality Assurance

### Badges de Qualidade

![Tests](https://img.shields.io/badge/Tests-Passing-success)
![Coverage](https://img.shields.io/badge/Coverage-85%25-green)
![Code Quality](https://img.shields.io/badge/Code%20Quality-A-brightgreen)
![Security](https://img.shields.io/badge/Security-No%20Vulnerabilities-success)

### CI/CD Pipeline

O projeto usa GitHub Actions para:
- ✅ Linting (Black, ESLint, Prettier)
- ✅ Type checking (mypy, TypeScript)
- ✅ Unit tests (pytest, Vitest)
- ✅ Integration tests
- ✅ Security scan (Bandit, npm audit)
- ✅ Build validation
- ✅ Deploy automático (staging/production)

---

## 📄 Licença

Este projeto está licenciado sob a **MIT License** - veja o arquivo [LICENSE](LICENSE) para detalhes.

```
MIT License

Copyright (c) 2025 Rafael Dourado

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 🌟 Agradecimentos

Agradecimentos especiais a todos que contribuíram para este projeto e às seguintes tecnologias open-source:

- [Django](https://www.djangoproject.com/) - Framework web robusto
- [React](https://react.dev/) - Biblioteca UI moderna
- [MediaMTX](https://github.com/bluenviron/mediamtx) - Servidor de streaming
- [FFmpeg](https://ffmpeg.org/) - Processamento de vídeo
- [PostgreSQL](https://www.postgresql.org/) - Banco de dados confiável
- [Redis](https://redis.io/) - Cache e messaging
- [RabbitMQ](https://www.rabbitmq.com/) - Message broker
- [Celery](https://docs.celeryq.dev/) - Task queue distribuída

---

## 📞 Contato e Suporte

### 👨‍💻 Desenvolvedor

**Rafael Dourado**

- 📧 **Email**: [rafaeldouradoc7@gmail.com](mailto:rafaeldouradoc7@gmail.com)
- 💼 **LinkedIn**: [rafael-dourado-dev](https://www.linkedin.com/in/rafael-dourado-dev/)
- 🐙 **GitHub**: [@rafaeldourado8](https://github.com/rafaeldourado8)

### 🐛 Reportar Bugs

Encontrou um bug? Abra uma [issue no GitHub](https://github.com/rafaeldourado8/vigilancia-system/issues) com:
- Descrição clara do problema
- Passos para reproduzir
- Comportamento esperado vs atual
- Screenshots/logs (se aplicável)
- Versão do sistema operacional e Docker

### 💡 Sugestões de Features

Tem uma ideia? Adoraríamos ouvir! Abra uma [feature request](https://github.com/rafaeldourado8/vigilancia-system/issues/new?template=feature_request.md).

### 🆘 Precisa de Ajuda?

- 📖 Consulte a [documentação completa](./docs/)
- 💬 Abra uma [discussão no GitHub](https://github.com/rafaeldourado8/vigilancia-system/discussions)
- 📧 Entre em contato via email

---

## 🗺️ Roadmap

### 📅 Versão 2.0 (Q2 2025)

- [ ] Reconhecimento facial com biometria
- [ ] Análise comportamental (detecção de quedas, intrusão)
- [ ] Busca semântica de vídeos com IA
- [ ] App mobile nativo (React Native)
- [ ] Suporte para drones e câmaras móveis
- [ ] Edge computing com processamento local

### 📅 Versão 2.5 (Q4 2025)

- [ ] Integração com sistemas de alarme
- [ ] Predição de eventos com Machine Learning
- [ ] Suporte para câmaras térmicas
- [ ] API pública com rate limiting avançado
- [ ] Marketplace de plugins
- [ ] Multi-tenancy completo

---

## 📊 Estatísticas do Projeto

![GitHub stars](https://img.shields.io/github/stars/rafaeldourado8/vigilancia-system?style=social)
![GitHub forks](https://img.shields.io/github/forks/rafaeldourado8/vigilancia-system?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/rafaeldourado8/vigilancia-system?style=social)

![Lines of Code](https://img.shields.io/badge/Lines%20of%20Code-50k%2B-blue)
![Contributors](https://img.shields.io/badge/Contributors-Welcome-brightgreen)
![Commits](https://img.shields.io/github/commit-activity/m/rafaeldourado8/vigilancia-system)
![Last Commit](https://img.shields.io/github/last-commit/rafaeldourado8/vigilancia-system)

---

<div align="center">

## ⭐ Se este projeto foi útil, considere dar uma estrela!

**Desenvolvido com ❤️ por [Rafael Dourado](https://github.com/rafaeldourado8)**

[⬆ Voltar ao topo](#-sistema-de-vigilância-inteligente)

</div>

---

**© 2025 Rafael Dourado. Todos os direitos reservados.**
