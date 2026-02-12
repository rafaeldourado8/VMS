# Correção: Gravações Duplicadas

## Problema Identificado

O sistema estava gravando vídeos em **dois diretórios diferentes** simultaneamente:

```
recordings/
├── camera_1/          ← Serviço recorder.py (CORRETO)
│   └── 12_02_2026/
│       └── 12_39_04.mp4
│
└── cam_1/             ← MediaMTX (DUPLICADO)
    └── 2026-02-12/
        └── 12-38-52-104075.mp4.mp4
```

## Causa Raiz

Dois serviços estavam gravando simultaneamente:

1. **`services/recorder/recorder.py`** (CORRETO)
   - Formato: `/recordings/camera_{id}/{dd_mm_yyyy}/`
   - Exemplo: `camera_1/12_02_2026/12_39_04.mp4`

2. **MediaMTX** (DUPLICADO - via `services/streaming/main.py`)
   - Formato: `/recordings/cam_{id}/{yyyy-mm-dd}/`
   - Exemplo: `cam_1/2026-02-12/12-38-52-104075.mp4.mp4`

## Solução Aplicada

### 1. Desabilitada gravação no MediaMTX

Em `services/streaming/main.py`:

```python
# ANTES
config = {
    "record": True,
    "recordPath": "/recordings/%path/%Y-%m-%d/%H-%M-%S-%f.mp4",
    ...
}

# DEPOIS
config = {
    "record": False
}
```

### 2. Mantido apenas serviço `recorder` para gravação

O recorder continua ativo no docker-compose.yml gravando em:
- Path: `/recordings/camera_{id}/{dd_mm_yyyy}/`
- Segmentos de 1 minuto
- Formato MP4

## Como Aplicar a Correção

### 1. Reconstruir o serviço streaming
```bash
docker-compose build streaming
docker-compose up -d streaming
```

### 2. Limpar gravações duplicadas do MediaMTX
```bash
scripts\cleanup_duplicate_recordings.bat
```

## Verificação

Após aplicar a correção, apenas o diretório `camera_X` deve receber novas gravações:

```bash
tree /f recordings
```

Resultado esperado:
```
recordings/
└── camera_1/
    └── 12_02_2026/
        └── 12_39_04.mp4
```

## Serviços que Dependem de Gravações

Atualizar os seguintes serviços para usar o formato `camera_{id}`:

- **recording** (API de consulta) - Ajustar path para `/recordings/camera_{id}/`
- **storage** (Indexador) - Indexar apenas `camera_*`
- **clips** (Gerador de clips) - Processar de `camera_*`

## Benefícios

✅ Elimina duplicação de armazenamento  
✅ Padroniza formato de diretórios  
✅ Reduz carga de I/O no disco  
✅ Simplifica manutenção  

## Observações

- O MediaMTX agora apenas faz streaming, não grava
- O recorder é responsável por toda gravação
- As gravações antigas em `cam_X` podem ser removidas com segurança
