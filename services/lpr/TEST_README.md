# Teste do Sistema LPR

## Problema Identificado

O serviço LPR estava iniciando mas não processava os frames porque:
1. O modelo YOLO não estava sendo inicializado corretamente no `lpr_stream.py`
2. Faltavam logs para debug
3. Erros estavam sendo silenciados

## Correções Aplicadas

### 1. `lpr_stream.py`
- ✅ Inicialização explícita do modelo YOLO
- ✅ Logs detalhados em cada etapa do processamento
- ✅ Tratamento de exceções com stack trace
- ✅ Salvamento de snapshots apenas quando detectar veículos
- ✅ Contador de frames e detecções

### 2. `lpr_manager.py`
- ✅ Uso correto do `rtsp_url` fornecido (sem sobrescrever)
- ✅ Logs mais detalhados

## Como Testar

### 1. Verificar se o serviço está rodando

```bash
docker-compose logs -f lpr_service
```

Você deve ver:
```
=== INICIANDO MONITORAMENTO ===
Thread iniciada
Loop criado
Conectando ao Redis...
Redis conectado!
Monitorando novas câmeras...
```

### 2. Publicar câmeras de teste

Primeiro, certifique-se de que o vídeo está sendo publicado no MediaMTX:

```bash
# Publicar vídeo no MediaMTX (câmera 999)
ffmpeg -re -stream_loop -1 -i ./1280_720_60fps.mp4 -c copy -f rtsp rtsp://localhost:8554/test_video
```

Em outro terminal, publique as câmeras no Redis:

```bash
cd tests
python test_lpr_cameras.py
```

### 3. Verificar logs do LPR

```bash
docker-compose logs -f lpr_service
```

Você deve ver:
```
Processando câmera 999
_start_lpr_sync chamado para 999
Criando LPRStreamService...
Input: rtsp://mediamtx:8554/test_video
Output: rtsp://mediamtx:8554/cam_999_ai
Iniciando service...
LPR iniciado para câmera 999
Abrindo stream: rtsp://mediamtx:8554/test_video
Stream aberto: 1280x720 @ 60fps
Iniciando FFmpeg para rtsp://mediamtx:8554/cam_999_ai
Iniciando loop de processamento para câmera 999
Processando frame 30 da câmera 999
Detectados 2 veículos no frame 30
Snapshot salvo: /app/snapshots/cam_999/20240115_143022_a1b2c3d4
```

### 4. Verificar snapshots gerados

```bash
cd tests
python check_snapshots.py
```

Você deve ver:
```
=== VERIFICANDO SNAPSHOTS ===

✓ Encontradas 2 câmeras

📷 cam_555
   └─ 15 detecções
      ├─ 20240115_143022_a1b2c3d4
      │  ├─ Tipo: car
      │  ├─ Confiança: 0.87
      │  ├─ Timestamp: 2024-01-15T14:30:22.123456
      │  ├─ Vehicle.jpg: ✓
      │  └─ Plate.jpg: ✗

📷 cam_999
   └─ 12 detecções
      ├─ 20240115_143025_e5f6g7h8
      │  ├─ Tipo: truck
      │  ├─ Confiança: 0.92
      │  ├─ Timestamp: 2024-01-15T14:30:25.654321
      │  ├─ Vehicle.jpg: ✓
      │  └─ Plate.jpg: ✗
```

### 5. Verificar stream anotado

O stream com as anotações estará disponível em:
- Câmera 999: `rtsp://localhost:8554/cam_999_ai`
- Câmera 555: `rtsp://localhost:8554/cam_555_ai`

Você pode visualizar com VLC ou FFplay:

```bash
ffplay rtsp://localhost:8554/cam_999_ai
```

## Estrutura dos Snapshots

Cada detecção gera uma pasta com:

```
snapshots/
└── cam_999/
    └── 20240115_143022_a1b2c3d4/
        ├── vehicle.jpg       # Recorte do veículo
        ├── full_frame.jpg    # Frame completo
        └── metadata.json     # Metadados da detecção
```

### Exemplo de metadata.json

```json
{
  "uuid": "a1b2c3d4",
  "camera_id": 999,
  "timestamp": "2024-01-15T14:30:22.123456",
  "vehicle_type": "car",
  "confidence": 0.87,
  "bbox": [100, 200, 300, 400]
}
```

## Troubleshooting

### Problema: "Falha ao abrir stream"

**Solução**: Verifique se o MediaMTX está recebendo o vídeo:
```bash
curl http://localhost:9997/v3/paths/list
```

### Problema: "Nenhuma detecção"

**Possíveis causas**:
1. Modelo YOLO não carregado corretamente
2. Vídeo sem veículos visíveis
3. Threshold de confiança muito alto

**Solução**: Verifique os logs detalhados:
```bash
docker-compose logs lpr_service | grep -i "detectados"
```

### Problema: "Snapshots não salvos"

**Solução**: Verifique permissões da pasta:
```bash
ls -la ./snapshots
docker-compose exec lpr_service ls -la /app/snapshots
```

## Próximos Passos

1. ✅ Detecção de veículos funcionando
2. ⏳ Detecção de placas (OCR)
3. ⏳ Salvamento de recortes de placas
4. ⏳ Integração com banco de dados
5. ⏳ API para consulta de detecções
