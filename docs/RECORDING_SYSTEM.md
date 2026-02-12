# Sistema de Gravação - VMS

## Arquitetura

```
               ┌──────────────┐
RTSP ───────▶  │  MediaMTX    │───▶ HLS LIVE
               └──────────────┘
                     │
                     │ (RTSP paralelo)
                     ▼
               ┌──────────────┐
               │   Recorder   │
               │ (FFmpeg)     │
               └──────────────┘
                     │
        ┌────────────┼─────────────┐
        ▼                            ▼
   Storage (Disco)            PostgreSQL
      (MP4 10s)                (Timeline)
```

## Responsabilidades

### MediaMTX
- ✅ APENAS streaming ao vivo
- ✅ RTSP → HLS
- ✅ Baixa latência
- ❌ Zero responsabilidade por gravação
- ❌ Zero timeline
- ❌ Zero playback

### Recorder
- ✅ 100% responsável por gravação
- ✅ Consome RTSP direto da câmera
- ✅ Segmenta arquivos (10s)
- ✅ Salva em disco
- ✅ Limpeza automática por retenção
- 🔜 Indexa no banco (timeline futura)

## Estrutura de Pastas

```
/recordings
 ├── cam_0001
 │   ├── 2026-02-08
 │   │   ├── 00-00-00.mp4
 │   │   ├── 00-00-10.mp4
 │   │   ├── 00-00-20.mp4
 │   │   └── ...
 │   ├── 2026-02-09
 │   │   ├── 14-32-00.mp4
 │   │   ├── 14-32-10.mp4
 │   │   └── ...
 │   └── 2026-02-10
 │       ├── 08-15-00.mp4
 │       └── ...
 │
 ├── cam_0002
 │   └── 2026-02-10
 │       ├── 09-00-00.mp4
 │       └── ...
```

## Retenção

- Configurável por câmera: 7, 15, 30 dias
- Limpeza automática a cada 1 hora
- Remove pastas de datas antigas
- Sem parar gravação
- Sem reiniciar serviço

## Segmentação

- Segmentos de 10 segundos
- Formato: `HH-MM-SS.mp4`
- Codec: copy (sem recodificação)
- Mudança de dia automática via strftime

## Exemplo de Uso

### Adicionar Câmera
```json
{
  "name": "Entrada Principal",
  "stream_url": "rtsp://admin:admin@192.168.1.100:554/stream",
  "location": "Portaria",
  "retention_days": 7
}
```

### Buscar Gravação
```
Usuário pede: cam_0001 — 2026-02-10 — 14:32:05

Backend:
1. Consulta banco (futuro)
2. Acha arquivo: 14-32-00.mp4
3. Offset: 5s
```

## Timeline (Futuro)

Será implementada posteriormente com:
- Indexação no PostgreSQL
- API de busca por timestamp
- Visualização de gaps
- Playback contínuo
