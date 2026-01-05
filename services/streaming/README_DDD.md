# Streaming Service - Arquitetura DDD

## 📁 Estrutura

```
streaming/
├── domain/                   # Domain Layer
│   └── streaming/
│       ├── entities/         # Stream
│       ├── value_objects/    # StreamPath, HLSUrl
│       ├── repositories/     # StreamRepository (interface)
│       └── exceptions.py
│
├── application/              # Application Layer (CQRS)
│   └── streaming/
│       ├── commands/         # ProvisionStream, RemoveStream
│       ├── queries/          # GetStreamStatus
│       └── handlers/         # Use cases
│
├── infrastructure/           # Infrastructure Layer
│   ├── mediamtx/            # MediaMTX HTTP client
│   └── repositories/        # InMemoryStreamRepository
│
├── api/                      # FastAPI routes
│   └── main_ddd.py          # API refatorada com DDD
│
└── tests/                    # Testes
    ├── unit/                # Domain + Application
    └── integration/         # Infrastructure
```

## 🎯 Domain Layer

### Entidades
- **Stream**: Representa um stream de vídeo
  - Métodos: `start()`, `stop()`, `mark_error()`, `is_active()`, `add_viewer()`, `remove_viewer()`
  - CC: 1-2 por método

### Value Objects
- **StreamPath**: Path do stream no MediaMTX (formato: `cam_{id}`)
- **HLSUrl**: URL HLS completa

### Repositórios
- **StreamRepository**: Interface com 5 métodos

## 🎯 Application Layer (CQRS)

### Commands
- **ProvisionStreamCommand**: Provisionar novo stream
- **RemoveStreamCommand**: Remover stream

### Queries
- **GetStreamStatusQuery**: Obter status do stream

### Handlers
- **ProvisionStreamHandler**: Valida duplicação, cria stream
- **RemoveStreamHandler**: Valida existência, remove stream

## 🎯 Infrastructure Layer

### MediaMTX Client
- HTTP client para MediaMTX API v3
- Métodos: `add_path()`, `remove_path()`, `get_path_status()`

### Repositórios
- **InMemoryStreamRepository**: Implementação em memória

## 🧪 Testes

### Executar Testes
```bash
# Todos os testes
run_streaming_tests.bat

# Apenas domain
cd services/streaming
python -m pytest tests/unit/domain/ -v

# Apenas application
python -m pytest tests/unit/application/ -v

# Apenas integração
python -m pytest tests/integration/ -v
```

### Métricas
- **Testes**: 23 (15 domain + 3 application + 5 integration)
- **CC**: < 3
- **Cobertura**: > 80%

## 🚀 API Endpoints

### POST /cameras/provision
Provisiona um novo stream

**Request:**
```json
{
  "camera_id": 1,
  "rtsp_url": "rtsp://camera.com/stream",
  "name": "Camera 1",
  "on_demand": true
}
```

**Response:**
```json
{
  "success": true,
  "camera_id": 1,
  "stream_path": "cam_1",
  "hls_url": "http://localhost:8889/cam_1/index.m3u8",
  "message": "Stream provisionado com sucesso"
}
```

### DELETE /cameras/{camera_id}
Remove um stream

### GET /cameras/{camera_id}/status
Obtém status de um stream

### GET /streams
Lista todos os streams

## 📊 Benefícios DDD

- ✅ Lógica de negócio isolada
- ✅ Testabilidade (mocks fáceis)
- ✅ Baixa complexidade (CC < 3)
- ✅ Separação de responsabilidades
- ✅ Fácil manutenção

## 🔄 Migração

A API antiga (`main.py`) continua funcionando. A nova API DDD está em `api/main_ddd.py`.

Para migrar:
1. Testar nova API
2. Atualizar frontend para usar novos endpoints
3. Deprecar API antiga
