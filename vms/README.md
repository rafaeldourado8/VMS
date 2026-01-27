# VMS - Video Management System

Sistema profissional de gerenciamento de vídeo com streaming, gravação cíclica e mosaicos.

## Arquitetura

- **Backend:** Django + FastAPI
- **Streaming:** MediaMTX (HLS low-latency)
- **Cache:** Redis
- **Database:** PostgreSQL
- **Proxy:** NGINX
- **Frontend:** HLS.js player

## Estrutura

```
vms/
├── src/                          # Código fonte
│   ├── config/                   # Django settings
│   ├── shared/                   # Domínio (DDD)
│   │   ├── admin/                # Cidades e Câmeras
│   │   └── streaming/            # Streaming, Recording, Mosaicos
│   └── infrastructure/           # Implementações
│       ├── adapters/             # Adapters (MediaMTX, etc)
│       ├── cache/                # Redis managers
│       ├── observers/            # PathObserver
│       ├── repositories/         # Repositories (Django)
│       └── servers/              # MediaMTX config
├── frontend/                     # Player HLS
├── recordings/                   # Gravações (volume)
├── scripts/                      # Scripts de teste
└── docs/                         # Documentação

```

## Quick Start

```bash
# 1. Setup ambiente
cd scripts
setup_test_env.bat

# 2. Subir containers
docker-compose up -d

# 3. Acessar
# - API: http://localhost:8001/docs
# - Admin: http://localhost:8000/admin (admin/admin123)
# - Player: http://localhost/player.html
```

## API Endpoints

### Streaming
- `POST /api/v1/streams` - Iniciar stream
- `DELETE /api/v1/streams/{id}` - Parar stream
- `GET /api/v1/streams` - Listar streams

### Recording
- `PUT /api/v1/cameras/{id}/recording` - Habilitar gravação
- `DELETE /api/v1/cameras/{id}/recording` - Desabilitar gravação
- `GET /api/v1/cameras/{id}/recording` - Status gravação

### Mosaics
- `POST /api/v1/mosaics` - Criar mosaico (máx 4 streams)
- `GET /api/v1/mosaics/{id}` - Obter mosaico
- `POST /api/v1/mosaics/{id}/streams/{session_id}` - Adicionar stream
- `DELETE /api/v1/mosaics/{id}/streams/{session_id}` - Remover stream

### System
- `GET /health` - Health check

## Protocolos Suportados

- **RTSP** - Câmeras IP tradicionais
- **RTMP** - Streaming servers
- **IP** - HTTP/HTTPS streams
- **P2P** - Protocolo proprietário

Todos convertidos para HLS automaticamente.

## Gravação Cíclica

- Segmentos de 30 minutos
- Formato fmp4 (low-latency)
- Limpeza automática após 7 dias
- Storage: `/recordings/stream_{camera_id}/`

## Multi-Tenant

- Isolamento por `city_id`
- Headers obrigatórios: `X-City-ID`, `X-User-ID`
- Permissões: SUPERADMIN, GESTOR, USER

## Documentação

- [PASSO 1 - Tenant (City)](docs/tenant/README.md)
- [PASSO 2 - Camera](docs/camera/README.md)
- [PASSO 3 - Repository](docs/repository/README.md)
- [PASSO 4 - Middleware](docs/middleware/README.md)
- [PASSO 5 - Streaming](docs/streaming/README.md)
- [PASSO 6 - Mosaicos](docs/streaming/PASSO6.md)
- [PASSO 7 - Gravação](docs/streaming/PASSO7.md)

## Tecnologias

- Python 3.12
- Django 5.x
- FastAPI
- MediaMTX v1.15.6
- PostgreSQL 16
- Redis 7
- NGINX Alpine
- Docker Compose

## License

Proprietary
