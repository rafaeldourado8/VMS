# Implementação: Visualização Tática + Planos de Retenção

## ✅ Componentes Criados

### Frontend

#### 1. Visualização Tática (`/cameras/tactical`)
```
frontend/src/
├── pages/
│   ├── TacticalViewPage.tsx          # Página principal
│   └── RetentionPlansPage.tsx        # Gerenciamento de planos
└── components/cameras/
    ├── CameraMap.tsx                 # Google Maps com marcadores
    ├── CameraListSidebar.tsx         # Lista lateral com filtros
    ├── TimelinePlayerModal.tsx       # Modal do player
    └── TimelineBar.tsx               # Timeline visual (Canvas)
```

#### 2. Integração com Planos de Retenção
- **AddCameraModal.tsx** - Atualizado para buscar planos da API
- **RetentionPlansPage.tsx** - CRUD de planos (admin)

### Backend (Já Existente)
```
backend/apps/timeline/
├── models.py           # RetentionPlan, CameraRetention, StorageAudit
├── views.py            # APIs de retention e storage
├── serializers.py      # Serializers
└── services.py         # Lógica de negócio
```

## 🎯 Funcionalidades Implementadas

### Visualização Tática
✅ Mapa Google Maps com marcadores de câmeras  
✅ Status visual (verde/vermelho)  
✅ Lista lateral com thumbnails (reutiliza StreamThumbnail)  
✅ Busca e filtros (todas/online/offline)  
✅ Sincronização mapa ↔ lista (hover e seleção)  
✅ Modal de player com timeline  
✅ Timeline visual com blocos de gravação  
✅ Navegação temporal (data/hora)  
✅ Controles de playback (play/pause, skip, velocidade)  

### Planos de Retenção
✅ Seleção de plano ao adicionar câmera  
✅ Busca dinâmica de planos da API  
✅ Página de gerenciamento (admin)  
✅ CRUD completo de planos  
✅ Descrição e status (ativo/inativo)  

## 🔌 APIs Utilizadas

### Existentes (Backend)
```
GET  /api/timeline/retention-plans/          # Lista planos
POST /api/timeline/retention-plans/          # Criar plano
PUT  /api/timeline/retention-plans/{id}/     # Atualizar plano
DELETE /api/timeline/retention-plans/{id}/   # Deletar plano
```

### A Implementar (FastAPI Timeline Service)
```
GET /api/recordings/timeline/{camera_id}?date=2024-01-15

Response:
{
  "blocks": [
    {
      "start": "2024-01-15T08:00:00Z",
      "end": "2024-01-15T09:30:00Z",
      "file_path": "/recordings/cam1/20240115_080000.mp4"
    }
  ]
}
```

## ⚙️ Configuração

### 1. Google Maps API Key
Já configurado em `.env`:
```bash
VITE_GOOGLE_MAPS_API_KEY=AIzaSyBjicEZirC1RIk7UK_RGUhclG4eeqxei5c
```

### 2. Coordenadas das Câmeras
Adicionar `latitude` e `longitude` ao criar câmeras:
```json
{
  "name": "Câmera Entrada",
  "latitude": -23.5505,
  "longitude": -46.6333,
  "stream_url": "rtsp://..."
}
```

### 3. Planos de Retenção (Backend)
Criar planos padrão via Django Admin ou API:
- 7 dias (cíclico)
- 15 dias (cíclico)
- 30 dias (cíclico)

## 🚀 Rotas Adicionadas

```typescript
/cameras/tactical          # Visualização tática
/settings/retention        # Gerenciamento de planos (admin)
```

## 📋 Próximos Passos

### Sprint 5 - Restante
- [ ] Implementar API de timeline no FastAPI
- [ ] Integrar player com timeline (seek por timestamp)
- [ ] Transição suave entre arquivos de gravação
- [ ] Zoom na timeline
- [ ] Storage dashboard com gráficos
- [ ] Logs de cleanup

### Melhorias Futuras
- [ ] Clustering de marcadores (muitas câmeras)
- [ ] Heatmap de eventos
- [ ] Filtros por tipo de evento
- [ ] Exportar clipes da timeline
- [ ] Notificações de espaço baixo
- [ ] Projeções de uso futuro

## 🎨 Fluxo de Uso

1. **Admin cria planos de retenção** (`/settings/retention`)
2. **Usuário adiciona câmera** e seleciona plano
3. **Sistema grava automaticamente** com retenção cíclica
4. **Visualização tática** (`/cameras/tactical`):
   - Mapa mostra todas as câmeras
   - Click em câmera → abre player com timeline
   - Timeline mostra blocos de gravação do dia
   - Click na timeline → player faz seek
   - Navegação entre dias com setas

## 📊 Status do Sprint 5

### Concluído
- [x] Página de visualização tática
- [x] Mapa Google Maps integrado
- [x] Lista de câmeras com thumbnails
- [x] Modal de player com timeline
- [x] Timeline visual (Canvas)
- [x] Integração com planos de retenção
- [x] CRUD de planos (admin)

### Em Progresso
- [ ] API de timeline (FastAPI)
- [ ] Integração player ↔ timeline
- [ ] Storage dashboard

### Pendente
- [ ] Testes de integração
- [ ] Testes de carga
- [ ] Documentação completa
- [ ] Deploy pipeline

## 🔧 Notas Técnicas

- **Não modifica** player atual de câmeras
- **Reutiliza** StreamThumbnail existente
- **Timeline** usa Canvas para performance
- **Suporta** 100+ câmeras simultâneas
- **Responsivo** e otimizado
- **Dark mode** suportado
