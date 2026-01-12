# 📹 VMS - Sistema de Monitoramento com IA

Sistema de monitoramento de vídeo com detecção de placas veiculares (LPR) e busca retroativa em gravações.

---

## 🚀 Quick Start

```bash
# 1. Clone o repositório
git clone <repo-url>
cd VMS

# 2. Configure variáveis de ambiente
cp .env.example .env

# 3. Inicie os serviços
docker-compose up -d

# 4. Acesse
Frontend: http://localhost:5173
Backend: http://localhost:8000
Prometheus: http://localhost:9090
```

---

## 📋 Documentação

### Principal
- **[📚 Índice Completo](docs/INDEX.md)** - Toda documentação organizada
- **[📋 Tasks](docs/TASKS.md)** - Tarefas por fase
- **[📊 Resumo do Projeto](docs/PROJECT_SUMMARY.md)** - Visão geral completa
- **[🏗️ Diagrama de Arquitetura](docs/ARCHITECTURE_DIAGRAM.excalidraw.json)** - Abrir no Excalidraw

### Por Serviço
- **[LPR Detection](services/lpr_detection/)** - YOLO + OCR para placas
- **[Streaming](services/streaming/)** - MediaMTX + HLS
- **[Backend](backend/)** - Django API

---

## 🏗️ Arquitetura

### Componentes

```
📹 Câmeras
  ├─ RTSP (LPR) → Alta definição → IA ativa
  └─ RTMP (Bullets) → Padrão → Apenas gravação
         ↓
🎥 MediaMTX → Streaming + Gravação contínua
         ↓
💾 Recording Service → Gravação cíclica (7/15/30 dias)
         ↓
🤖 LPR Detection → YOLO + OCR (apenas RTSP)
         ↓
🔍 Sentinela → Busca retroativa em gravações
         ↓
🔧 Backend → API REST
         ↓
🎨 Frontend → React + Vite
```

---

## 📹 Tipos de Câmeras

### RTSP (LPR) - Alta Definição
- **Protocolo**: `rtsp://`
- **Quantidade**: 10-20 por cidade
- **IA**: ✅ Ativa (YOLO + OCR)
- **Gravação**: ✅ Contínua

### RTMP (Bullets) - Padrão
- **Protocolo**: `rtmp://`
- **Quantidade**: até 1000 por cidade
- **IA**: ❌ Desativada
- **Gravação**: ✅ Contínua

---

## 💾 Sistema de Armazenamento

### Gravação Cíclica

| Plano | Dias | Usuários | Diferencial |
|-------|------|----------|-------------|
| Basic | 7    | 3        | -           |
| Pro   | 15   | 5        | -           |
| Premium | 30 | 10       | Relatórios  |

### Clipes Permanentes
- Usuário cria clipe de gravação
- Clipe **não é deletado** no ciclo
- Armazenamento permanente

---

## 🔍 Sentinela (Busca Retroativa)

Busca em gravações (não tempo real):
- 🚗 Veículos: cor, tipo, marca
- 🔢 Placas: OCR
- 📅 Por data e câmera
- ⏱️ Resultados com timestamp

---

## 🛠️ Stack Tecnológica

### Backend
- Django 4.2
- PostgreSQL 15
- Redis 7
- RabbitMQ 3.13

### Frontend
- React 18
- Vite 5
- TailwindCSS
- TypeScript

### Streaming
- MediaMTX (HLS/WebRTC)
- FFmpeg

### IA
- YOLOv8n (detecção)
- Fast-Plate-OCR (reconhecimento)
- PyTorch (CPU-only)

### Infraestrutura
- Docker Compose
- Prometheus
- HAProxy
- Kong Gateway

---

## 📊 Status do Projeto

### ✅ Concluído
- [x] Streaming (MediaMTX + HLS)
- [x] Backend API (Django)
- [x] Frontend (React)
- [x] LPR Detection (YOLO + OCR)
- [x] Monitoring (Prometheus)

### 🔄 Em Andamento
- [ ] Recording Service (gravação cíclica)
- [ ] Playback & Timeline
- [ ] UI Refactor

### ❌ Pendente
- [ ] Sentinela (busca retroativa)
- [ ] Sistema de Planos
- [ ] Gerenciamento de Usuários

---

## 🧪 Testes

```bash
# Testar LPR Detection
cd tests
python test_failover.py

# Testar auto-restart
python test_auto_restart.py

# Testar câmeras reais
python test_real_cameras.py
```

Ver [docs/TEST_FAILOVER.md](docs/TEST_FAILOVER.md) para guia completo.

---

## 📦 Estrutura do Projeto

```
VMS/
├── backend/              # Django API
├── frontend/             # React + Vite
├── services/
│   ├── lpr_detection/   # YOLO + OCR
│   ├── streaming/       # MediaMTX integration
│   └── ai_detection/    # Rekognition (opcional)
├── docs/                # Documentação
├── tests/               # Scripts de teste
├── config/              # Configurações
├── legacy/              # Código legado
└── docker-compose.yml   # Orquestração
```

---

## 🔧 Configuração

### Variáveis de Ambiente

```bash
# Backend
POSTGRES_USER=vms_user
POSTGRES_PASSWORD=secure_password
POSTGRES_DB=vms_db

# LPR Detection
ADMIN_API_KEY=your_api_key

# MediaMTX
MEDIAMTX_API_USER=mediamtx_api_user
MEDIAMTX_API_PASS=secure_password
```

Ver `.env.example` para lista completa.

---

## 📞 Suporte

### Logs
```bash
docker-compose logs -f [service]
```

### Health Checks
```bash
curl http://localhost:8000/health  # Backend
curl http://localhost:5000/health  # LPR Detection
curl http://localhost:8001/health  # Streaming
```

### Restart
```bash
docker-compose restart [service]
```

---

## 📝 Contribuindo

1. Leia [docs/TASKS.md](docs/TASKS.md)
2. Escolha uma task
3. Crie branch: `git checkout -b feature/task-name`
4. Commit: `git commit -m "feat: description"`
5. Push: `git push origin feature/task-name`
6. Abra Pull Request

---

## 📄 Licença

[Definir licença]

---

## 🔗 Links Úteis

- [Documentação Completa](docs/INDEX.md)
- [Diagrama de Arquitetura](docs/ARCHITECTURE_DIAGRAM.excalidraw.json)
- [Guia de Testes](docs/TEST_FAILOVER.md)
- [MediaMTX Docs](https://github.com/bluenviron/mediamtx)
- [YOLOv8 Docs](https://docs.ultralytics.com/)
