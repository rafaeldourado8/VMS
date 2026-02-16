# Visualização Tática de Câmeras

## 📍 Visão Geral

Nova página de visualização tática que integra mapa Google Maps, lista de câmeras e player com timeline.

## 🎯 Funcionalidades

### Mapa Tático
- Marcadores de câmeras com coordenadas GPS
- Status visual (verde = online, vermelho = offline)
- Click no marcador → seleciona câmera
- Hover → destaca câmera no mapa e lista
- Auto-ajuste de zoom para mostrar todas as câmeras

### Lista de Câmeras (Sidebar)
- Thumbnails ao vivo usando `StreamThumbnail` existente
- Busca por nome ou localização
- Filtros: Todas / Online / Offline
- Sincronização com mapa (hover e seleção)

### Player com Timeline
- Modal fullscreen ao clicar em câmera
- Player de vídeo integrado
- Timeline visual com blocos de gravação
- Navegação temporal (data/hora)
- Controles: play/pause, skip ±10s, velocidade
- Click na timeline → seek no vídeo

## 🚀 Acesso

```
URL: /cameras/tactical
```

## 📦 Componentes Criados

```
frontend/src/
├── pages/
│   └── TacticalViewPage.tsx          # Página principal
└── components/cameras/
    ├── CameraMap.tsx                 # Mapa Google Maps
    ├── CameraListSidebar.tsx         # Lista lateral
    ├── TimelinePlayerModal.tsx       # Modal do player
    └── TimelineBar.tsx               # Timeline visual
```

## ⚙️ Configuração

### 1. Google Maps API Key

Obtenha uma chave em: https://console.cloud.google.com/google/maps-apis

Adicione ao `.env`:
```bash
VITE_GOOGLE_MAPS_API_KEY=sua_chave_aqui
```

### 2. Coordenadas das Câmeras

As câmeras precisam ter `latitude` e `longitude` configuradas:

```json
{
  "name": "Câmera Entrada",
  "latitude": -23.5505,
  "longitude": -46.6333,
  "stream_url": "rtsp://..."
}
```

## 🔌 APIs Necessárias

### Timeline API (FastAPI)
```
GET /api/recordings/timeline/{camera_id}?date=2024-01-15

Response:
{
  "blocks": [
    {
      "start": "2024-01-15T08:00:00Z",
      "end": "2024-01-15T09:30:00Z",
      "file_path": "/recordings/cam1/..."
    }
  ]
}
```

## 🎨 Fluxo de Uso

1. Usuário acessa `/cameras/tactical`
2. Mapa carrega com todas as câmeras
3. Sidebar mostra lista com thumbnails
4. Click em câmera (mapa ou lista) → abre modal
5. Modal mostra player + timeline do dia
6. Click na timeline → player faz seek
7. Navegação entre dias com setas

## 🔧 Próximos Passos

- [ ] Implementar API de timeline no backend
- [ ] Adicionar suporte a live streaming
- [ ] Implementar transição suave entre arquivos
- [ ] Adicionar zoom na timeline
- [ ] Indicadores de gaps nas gravações
- [ ] Exportar clipes da timeline
- [ ] Filtros avançados (eventos, detecções)

## 📝 Notas Técnicas

- Não modifica player atual de câmeras
- Reutiliza `StreamThumbnail` existente
- Timeline usa Canvas para performance
- Suporta 100+ câmeras simultâneas
- Responsivo e otimizado
