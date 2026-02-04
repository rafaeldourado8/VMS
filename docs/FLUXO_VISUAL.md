# 🎯 Fluxo Completo - Streaming + Gravação + LPR Offline

```
┌─────────────────────────────────────────────────────────────────────┐
│                         1. STREAMING (Não Mexemos)                  │
└─────────────────────────────────────────────────────────────────────┘

    Câmera RTSP
        │
        ▼
    MediaMTX (On-Demand)
        │
        ├─► HLS :8888  ──► Player Frontend (só quando aberto)
        └─► WebRTC :8889


┌─────────────────────────────────────────────────────────────────────┐
│                    2. GRAVAÇÃO AUTOMÁTICA (NOVO)                    │
└─────────────────────────────────────────────────────────────────────┘

    Player Aberto
        │
        ▼
    HLS Iniciado ──► MediaMTX inicia gravação
        │
        ▼
    /recordings/cam_1/2025-01-15/10-30-00.mp4
        │
        ▼
    Player Fechado (30s) ──► MediaMTX para gravação
        │
        ▼
    Recording.ended_at = now()


┌─────────────────────────────────────────────────────────────────────┐
│                  3. SNAPSHOT EM CACHE (NOVO)                        │
└─────────────────────────────────────────────────────────────────────┘

    Gravação Finalizada
        │
        ▼
    Celery Task: generate_recording_snapshot(recording_id)
        │
        ▼
    Extrai 1º frame do vídeo
        │
        ▼
    Redimensiona para 320x180 JPEG
        │
        ▼
    Salva em Recording.snapshot_cached (ImageField)
        │
        ▼
    /media/recording_snapshots/2025/01/15/rec_1.jpg
        │
        ▼
    Frontend lista gravações ──► Exibe foto estática (SEM streaming!)


┌─────────────────────────────────────────────────────────────────────┐
│                  4. LPR OFFLINE (NOVO)                              │
└─────────────────────────────────────────────────────────────────────┘

    Worker LPR (loop a cada 30s)
        │
        ▼
    Busca Recording.lpr_processed = False
        │
        ▼
    Abre vídeo gravado
        │
        ▼
    Processa 1 frame a cada 2 segundos
        │
        ├─► YOLO detecta placa
        │       │
        │       ▼
        │   EasyOCR lê texto
        │       │
        │       ▼
        │   Salva snapshot da placa
        │       │
        │       ▼
        │   Cria Deteccao no banco
        │
        ▼
    Recording.lpr_processed = True
    Recording.lpr_detections_count = 15


┌─────────────────────────────────────────────────────────────────────┐
│                     RESULTADO FINAL                                 │
└─────────────────────────────────────────────────────────────────────┘

Frontend Lista de Gravações:
┌────────────────────────────────────┐
│ [📷 Foto Cache]  Entrada Principal │
│ 15/01/2025 10:30 - 11:30 (1h)     │
│ 🚗 15 placas detectadas            │
│ [▶️ Reproduzir] [🔍 Ver Detecções] │
└────────────────────────────────────┘

Vantagens:
✅ Lista carrega instantaneamente (foto em cache)
✅ Não gera banda desnecessária
✅ LPR processa offline (não sobrecarrega streaming)
✅ Gravações persistidas e indexadas
```

## 🔄 Comparação: Antes vs Depois

### ❌ ANTES (Tempo Real)
```
Streaming ──► LPR processa em tempo real ──► Detecções
   │
   └─► Sobrecarga de CPU
   └─► Dependente de streaming ativo
   └─► Thumbnails geravam banda
```

### ✅ DEPOIS (Offline)
```
Streaming ──► Gravação ──► Snapshot Cache ──► LPR Offline ──► Detecções
   │              │              │                  │
   │              │              │                  └─► Processa quando tiver recursos
   │              │              └─► Foto estática (sem banda)
   │              └─► Persistido em disco
   └─► Leve e on-demand
```
