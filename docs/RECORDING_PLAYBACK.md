# Sistema de Gravação e Playback - GT-Vision VMS

## Arquitetura

### Componentes

1. **MediaMTX** - Servidor de streaming e gravação
   - Porta 8888: HLS live streaming
   - Porta 9996: Playback server (gravações)
   - Porta 9997: API de controle
   - Grava automaticamente em `/recordings/cam_X/YYYY-MM-DD/HH-MM-SS.mp4`

2. **Backend Django** - API de listagem de gravações
   - Endpoint: `GET /api/cameras/recordings/`
   - Escaneia filesystem e retorna gravações disponíveis

3. **Frontend React** - Interface de playback
   - Componente `RecordingPlayer`: Seletor de data/hora + player
   - Integrado na página de Detecções

## Fluxo de Gravação

```
Câmera RTSP → MediaMTX → Gravação Automática
                ↓
        /recordings/cam_1/2025-01-20/14-30-00.mp4
```

### Configuração de Gravação (mediamtx.yml)

```yaml
pathDefaults:
  record: yes                                    # Gravação habilitada
  recordPath: /recordings/%path/%Y-%m-%d/%H-%M-%S-%f
  recordFormat: fmp4                             # Formato otimizado
  recordPartDuration: 1s                         # Segmentos de 1s
  recordSegmentDuration: 24h                     # Arquivo por dia
  recordDeleteAfter: 168h                        # Retenção: 7 dias (configurável)
```

### Estrutura de Diretórios

```
/recordings/
├── cam_1/
│   ├── 2025-01-20/
│   │   ├── 00-00-00.mp4  (00:00 - 23:59)
│   │   └── ...
│   ├── 2025-01-21/
│   └── ...
├── cam_2/
└── ...
```

## Fluxo de Playback

```
Frontend → Django API → Filesystem Scan → Lista de Gravações
    ↓
Usuário seleciona gravação
    ↓
Frontend → MediaMTX Playback Server (9996) → HLS Stream
```

### API de Listagem

**Request:**
```http
GET /api/cameras/recordings/?camera_id=1&date=2025-01-20&start_time=14:00&end_time=16:00
Authorization: Bearer <token>
```

**Response:**
```json
{
  "camera_id": 1,
  "date": "2025-01-20",
  "recordings": [
    {
      "filename": "14-30-00.mp4",
      "start_time": "14:30:00",
      "size_mb": 125.5,
      "playback_url": "/cam_1/2025-01-20/14-30-00.mp4/index.m3u8"
    }
  ],
  "total_size_mb": 500.2,
  "total_duration_seconds": 14400
}
```

### Playback URL

```
http://localhost:9996/playback/cam_1/2025-01-20/14-30-00.mp4/index.m3u8
```

MediaMTX serve o arquivo gravado como HLS sem necessidade de conversão.

## Interface do Usuário

### Página de Detecções

1. **Botão "Ver Gravações"** - Alterna entre detecções e gravações
2. **Seletor de Câmera** - Grid com todas as câmeras disponíveis
3. **RecordingPlayer Component:**
   - Calendário para selecionar data
   - Navegação dia anterior/próximo
   - Filtros de hora inicial/final
   - Lista de gravações disponíveis
   - Player HLS integrado

### Exemplo de Uso

1. Usuário clica em "Ver Gravações"
2. Seleciona câmera "Entrada Principal"
3. Escolhe data: 20/01/2025
4. Define período: 14:00 - 16:00
5. Lista mostra 2 gravações disponíveis
6. Clica em uma gravação → Player carrega automaticamente

## Escalabilidade

### Performance

- **Sem conversão**: MediaMTX serve arquivos fmp4 diretos
- **Cache**: Backend pode cachear lista de arquivos em Redis
- **Distribuído**: Cada câmera = pasta separada
- **Baixo overhead**: Backend só lista arquivos, não processa vídeo

### Capacidade

**Exemplo: 20 câmeras, 7 dias de retenção**

- Bitrate médio: 2 Mbps por câmera
- Armazenamento por câmera/dia: ~21 GB
- Total: 20 câmeras × 21 GB × 7 dias = **2.94 TB**

### Otimizações

1. **Retenção configurável**: Ajustar `recordDeleteAfter` no mediamtx.yml
2. **Bitrate adaptativo**: Configurar CRF/maxrate por câmera
3. **Gravação sob demanda**: Habilitar `record: yes` apenas em câmeras específicas
4. **Compressão**: Usar H.265 para reduzir 30-50% do espaço

## Configuração

### 1. Habilitar Gravação (mediamtx.yml)

```yaml
pathDefaults:
  record: yes
  recordDeleteAfter: 168h  # 7 dias
```

### 2. Ajustar Retenção

```yaml
recordDeleteAfter: 336h  # 14 dias
recordDeleteAfter: 720h  # 30 dias
```

### 3. Configurar por Câmera

```yaml
paths:
  cam_1:
    record: yes
    recordDeleteAfter: 720h  # 30 dias para câmera crítica
  
  cam_2:
    record: yes
    recordDeleteAfter: 168h  # 7 dias para câmera normal
```

### 4. Frontend (.env)

```bash
VITE_PLAYBACK_URL=http://localhost:9996
```

## Monitoramento

### Espaço em Disco

```bash
# Verificar uso do volume
docker exec gtvision_mediamtx du -sh /recordings

# Por câmera
docker exec gtvision_mediamtx du -sh /recordings/cam_*
```

### Gravações Ativas

```bash
# Listar arquivos sendo gravados
docker exec gtvision_mediamtx ls -lh /recordings/cam_1/$(date +%Y-%m-%d)/
```

## Troubleshooting

### Gravações não aparecem

1. Verificar se gravação está habilitada: `record: yes`
2. Verificar permissões do volume: `mediamtx_recordings`
3. Verificar logs: `docker logs gtvision_mediamtx`

### Player não carrega

1. Verificar porta 9996 exposta no docker-compose.yml
2. Verificar CORS no MediaMTX (já configurado)
3. Verificar URL no navegador: `http://localhost:9996/playback/cam_1/...`

### Espaço em disco cheio

1. Reduzir `recordDeleteAfter`
2. Reduzir bitrate: `maxrate: 1M` no mediamtx.yml
3. Desabilitar gravação em câmeras não críticas

## Próximas Melhorias

1. **Timeline visual**: Canvas com segmentos de gravação
2. **Exportação de clips**: Recortar e baixar trechos específicos
3. **Busca por evento**: Integrar com detecções de IA
4. **Multi-câmera sync**: Reproduzir múltiplas câmeras sincronizadas
5. **Thumbnails**: Gerar previews das gravações
6. **Configuração via UI**: Ajustar retenção por câmera no frontend

## Referências

- MediaMTX Docs: https://github.com/bluenviron/mediamtx
- MediaMTX Playback: https://github.com/bluenviron/mediamtx#playback-server
- HLS.js: https://github.com/video-dev/hls.js/
