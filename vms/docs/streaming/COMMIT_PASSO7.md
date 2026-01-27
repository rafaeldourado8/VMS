# COMMIT - PASSO 7: Gravação Cíclica + Path Observer + API v1

## Resumo
Implementado sistema completo de gravação cíclica com PathObserver, seguindo 3 regras de ouro para integração com MediaMTX. API versionada (v1) com contratos tipados e documentação OpenAPI.

## Arquivos Criados

### Domínio Recording
- `src/shared/streaming/recording/models.py` - RecordingSession, RecordingStatus
- `src/shared/streaming/recording/recording_manager.py` - Interface RecordingManager
- `src/shared/streaming/core/ports.py` - RecordingPort

### Adapters
- `src/infrastructure/adapters/recording/mock_recording_adapter.py` - Mock para testes
- `src/infrastructure/adapters/recording/mediamtx_recording_adapter.py` - Adapter real

### Manager
- `src/infrastructure/cache/streaming/redis_recording_manager.py` - Implementação Redis

### Path Observer
- `src/infrastructure/observers/path_observer.py` - Monitora paths do MediaMTX

### API
- `src/shared/streaming/stream/schemas.py` - Response models Pydantic
- `src/shared/streaming/recording/recording_endpoints.py` - Endpoints (deprecated)

### Documentação
- `docs/streaming/PASSO7.md` - Documentação completa
- `docs/streaming/COMMIT_PASSO7.md` - Este arquivo

### Scripts (movidos para /scripts)
- `scripts/test_recording_mock.bat`
- `scripts/test_passo7_final.bat`
- `scripts/test_path_observer.bat`
- `scripts/test_observer_complete.bat`
- `scripts/test_api_contracts.bat`

## Arquivos Modificados

### API
- `src/shared/streaming/stream/api.py` - Versionamento v1, response models, PathObserver
- `src/shared/streaming/stream/mosaic_endpoints.py` - Removido (integrado na api.py)

### Adapters
- `src/infrastructure/servers/mediamtx/adapter.py` - Adicionado get_all_paths()
- `src/infrastructure/servers/mediamtx/http_adapter.py` - Implementado get_all_paths()

### Models
- `src/shared/admin/cameras/models.py` - Campo recording_enabled
- Migration: `0004_camera_recording_enabled.py`

### Repositories
- `src/infrastructure/repositories/camera_repository.py` - update_recording_status()
- `src/infrastructure/repositories/django_camera_repository.py` - Implementação

### Streaming
- `src/infrastructure/cache/streaming/redis_streaming_manager.py` - Simplificado (3 regras)

### Config
- `src/infrastructure/servers/mediamtx.yml` - record: yes global
- `docker-compose.yml` - Volume /recordings

## Funcionalidades

### Gravação Cíclica
- ✅ Gravação automática via MediaMTX (record: yes global)
- ✅ Segmentos de 30 minutos (fmp4)
- ✅ Limpeza automática após 7 dias
- ✅ Storage path: /recordings/%path/

### Path Observer
- ✅ Monitora /v3/paths/list a cada 10s
- ✅ Detecta câmeras ONLINE (path criado)
- ✅ Detecta câmeras OFFLINE (path removido)
- ✅ Callbacks para lógica de negócio
- ✅ Integrado no FastAPI (startup/shutdown)

### API v1
- ✅ Versionamento /api/v1/
- ✅ Response models Pydantic
- ✅ Tags (Streaming, Recording, Mosaics, System)
- ✅ Documentação OpenAPI em /docs
- ✅ Health check real (MediaMTX + Redis)

### Endpoints Recording
- `PUT /api/v1/cameras/{id}/recording` - Habilitar
- `DELETE /api/v1/cameras/{id}/recording` - Desabilitar
- `GET /api/v1/cameras/{id}/recording` - Status

### Endpoints Streaming
- `POST /api/v1/streams` - Iniciar
- `DELETE /api/v1/streams/{id}` - Parar
- `GET /api/v1/streams` - Listar

### Endpoints Mosaics
- `POST /api/v1/mosaics` - Criar
- `GET /api/v1/mosaics/{id}` - Obter
- `POST /api/v1/mosaics/{id}/streams/{session_id}` - Adicionar
- `DELETE /api/v1/mosaics/{id}/streams/{session_id}` - Remover
- `DELETE /api/v1/mosaics/{id}` - Deletar

## 3 Regras de Ouro

1. **Backend NUNCA cria path**
   - MediaMTX cria automaticamente quando câmera conecta
   - Backend apenas registra sessão

2. **path not found NÃO é erro**
   - É estado normal (câmera offline)
   - Backend não falha, apenas informa

3. **path not found = câmera OFFLINE**
   - Informação de estado, não falha
   - PathObserver detecta e notifica

## Testes
- ✅ Mock adapter funcionando
- ✅ PathObserver detectando paths
- ✅ API v1 com contratos tipados
- ✅ Health check validando dependências
- ✅ Gravação automática configurada

## Organização
- ✅ Scripts movidos para /scripts
- ✅ Documentação completa em /docs
- ✅ Arquitetura DDD respeitada

## Próximo Passo
PASSO 8 - Player de Replay (listar gravações, player HLS, timeline)
