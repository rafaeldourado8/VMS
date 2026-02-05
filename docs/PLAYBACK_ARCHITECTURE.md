# Timeline de Playback - Arquitetura Segura

## Regra de Ouro

**NUNCA MEXER NO VideoPlayer.tsx** - Ele funciona em produção. É ouro.

## Arquitetura em Camadas

```
┌─────────────────────────────────┐
│      CameraViewer (novo)        │  ← Orquestra tudo
│  - Gerencia modo live/playback  │
│  - Troca o src do player        │
└─────────────────────────────────┘
           │         │
           ▼         ▼
    ┌──────────┐  ┌──────────────┐
    │VideoPlayer│  │PlaybackTimeline│
    │(intocado)│  │    (novo)     │
    └──────────┘  └──────────────┘
```

## Componentes Criados

### 1. PlaybackTimeline.tsx

Responsabilidades:
- Desenha timeline com canvas
- Mostra segmentos gravados (azul/vermelho/amarelo)
- Playhead (linha vermelha)
- Zoom temporal (24h/1h/5min)
- Navegação (setas)
- Emite evento: `onSeek(time: Date)`

**NÃO controla o player diretamente**

### 2. CameraViewer.tsx

Responsabilidades:
- Gerencia estado: `live` ou `playback`
- Troca o `src` do VideoPlayer
- Botão "Ao Vivo"
- Conecta Timeline → VideoPlayer

Fluxo:
```typescript
// LIVE
src = "/streaming/cameras/1/index.m3u8"

// PLAYBACK (usuário clica na timeline)
onSeek(time) → src = "/playback/camera/1/2026-02-05/07-35.m3u8"
```

### 3. PlaybackDemoPage.tsx

Exemplo de uso completo.

## Como Funciona

### Modo Live (padrão)
```tsx
<CameraViewer
  cameraId={1}
  liveUrl="/streaming/cameras/1/index.m3u8"
/>
```

- VideoPlayer recebe `liveUrl`
- Timeline mostra "agora"
- Botão "Ao Vivo" oculto

### Modo Playback (usuário clica na timeline)

1. Usuário clica na timeline às 14:35
2. Timeline emite: `onSeek(new Date('2026-02-05T14:35:00'))`
3. CameraViewer:
   - Muda modo para `playback`
   - Calcula novo src: `/playback/camera/1/2026-02-05/14-35.m3u8`
   - Atualiza `videoSrc`
4. VideoPlayer re-renderiza com novo src
5. Botão "Ao Vivo" aparece

### Voltar ao Vivo

1. Usuário clica "Ao Vivo"
2. CameraViewer:
   - Muda modo para `live`
   - Restaura `videoSrc = liveUrl`
3. VideoPlayer volta ao stream live

## O que o VideoPlayer NÃO sabe

- Se está em live ou playback
- Que existe uma timeline
- Que existe navegação temporal

**Ele só toca HLS. Sempre.**

## Backend Necessário

### Endpoint de Playback

```
GET /playback/camera/{id}/{date}/{time}.m3u8
```

Exemplo:
```
/playback/camera/1/2026-02-05/14-35.m3u8
```

Retorna:
- Manifest HLS apontando para segmentos daquele horário
- Gerado on-demand ou pré-processado

### Endpoint de Gravações

```
GET /api/cameras/{id}/recordings?date={date}
```

Retorna:
```json
[
  {
    "start": "2026-02-05T14:00:00Z",
    "end": "2026-02-05T15:30:00Z",
    "type": "continuous"
  },
  {
    "start": "2026-02-05T16:00:00Z",
    "end": "2026-02-05T16:05:00Z",
    "type": "event"
  }
]
```

## Funcionalidades Implementadas

- ✅ Navegação temporal (seek)
- ✅ Zoom (24h/1h/5min)
- ✅ Visualização de gravações
- ✅ Playhead (cursor vermelho)
- ✅ Timestamp atual
- ✅ Botão "Ao Vivo"
- ✅ Navegação por setas

## Funcionalidades Futuras (fácil adicionar)

- Exportar clipe (já tem prop `onExport`)
- Eventos na timeline (detecções IA)
- Múltiplas câmeras sincronizadas
- Velocidade de reprodução
- Frame a frame

## Vantagens desta Arquitetura

1. **Segurança**: VideoPlayer intocado
2. **Reversível**: Pode voltar atrás facilmente
3. **Testável**: Cada componente isolado
4. **Escalável**: Fácil adicionar features
5. **Manutenível**: Separação clara de responsabilidades

## Como Integrar em Produção

### Opção 1: Substituir gradualmente

```tsx
// Antes
<VideoPlayer src={liveUrl} />

// Depois
<CameraViewer cameraId={1} liveUrl={liveUrl} />
```

### Opção 2: Feature flag

```tsx
{usePlayback ? (
  <CameraViewer cameraId={1} liveUrl={liveUrl} />
) : (
  <VideoPlayer src={liveUrl} />
)}
```

### Opção 3: Rota separada

```tsx
// /cameras → VideoPlayer (atual)
// /playback → CameraViewer (novo)
```

## Testes Recomendados

1. Abrir em live → deve funcionar igual antes
2. Clicar na timeline → deve trocar para playback
3. Clicar "Ao Vivo" → deve voltar ao live
4. Trocar zoom → timeline deve ajustar
5. Navegar com setas → deve mover a view
6. Trocar de câmera → deve limpar buffers (já funciona)

## Monitoramento

```javascript
// Ver modo atual
console.log(mode) // 'live' ou 'playback'

// Ver src atual
console.log(videoSrc)

// Ver tempo de playback
console.log(playbackTime)
```

## Próximos Passos

1. Integrar API real de gravações
2. Implementar backend de playback HLS
3. Adicionar exportação de clipes
4. Testar com dados reais
5. Adicionar eventos de IA na timeline
