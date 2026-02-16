# Timeline Service - Documentação MVP

## Visão Geral

O Timeline Service é composto por dois componentes principais:

### 1. FastAPI Service (`services/timeline/`)
**Responsabilidade**: Processamento de mídia e indexação de gravações

**O que FAZ:**
- 📂 Lê o filesystem (ou S3)
- 🧾 Indexa gravações (por câmera / dia / horário)
- ⏱ Converte timestamp → arquivo correto
- 🎞 Decide qual vídeo tocar quando você clica na timeline
- 🧩 Gera blocos da timeline (intervalos gravados)
- ⚡ Tudo assíncrono (scan, ffprobe, stat)
- 🔁 Reindexa quando gravações entram ou saem

**O que NÃO faz:**
- ❌ Login
- ❌ Permissão
- ❌ Multi-tenant
- ❌ Regras de negócio do cliente
- ❌ UI

### 2. Django App (`backend/apps/timeline/`)
**Responsabilidade**: Configurações e API pública

**O que FAZ:**
- ⚙️ Configurações de retenção
- 📊 Auditoria
- 📡 API pública para frontend
- 🛠 Admin, painel, billing, etc

**O que NÃO faz:**
- ❌ Varredura pesada de disco
- ❌ Resolver vídeo por timestamp
- ❌ Processamento de mídia
- ❌ Lógica de timeline em baixo nível

## Arquitetura

```
Frontend → Django App → FastAPI Service → Filesystem/S3
    ↓         ↓              ↓
   UI    Configurações   Indexação
         Auditoria      Processamento
         Permissões     Timeline Logic
```

## Planos de Armazenamento

Cada câmera terá um plano de gravação cíclica:

- **7 dias**: Grava por 7 dias, depois apaga automaticamente
- **15 dias**: Grava por 15 dias, depois apaga automaticamente
- **30 dias**: Grava por 30 dias, depois apaga automaticamente
- **Personalizado**: Configuração customizada

## Sprints

- [Sprint 1: FastAPI Service Base](SPRINT_1.md)
- [Sprint 2: Django App Base](SPRINT_2.md)
- [Sprint 3: Indexação e Timeline](SPRINT_3.md)
- [Sprint 4: Retenção e Cleanup](SPRINT_4.md)
- [Sprint 5: Integração e Testes](SPRINT_5.md)

## APIs

### FastAPI Endpoints
- `GET /timeline/{camera_id}` - Timeline de uma câmera
- `GET /video/{camera_id}/{timestamp}` - Vídeo por timestamp
- `POST /reindex/{camera_id}` - Forçar reindexação
- `GET /blocks/{camera_id}` - Blocos de gravação

### Django Endpoints
- `GET /api/timeline/cameras/` - Lista câmeras com configuração
- `POST /api/timeline/cameras/{id}/retention/` - Configurar retenção
- `GET /api/timeline/storage/` - Status de armazenamento
- `GET /api/timeline/audit/` - Log de auditoria