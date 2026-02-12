# VMS - Video Management System

Sistema de gerenciamento de vídeo com detecção de placas (LPR) e streaming RTSP.

## Estrutura do Projeto

```
VMS/
├── backend/          # Django API
├── frontend/         # React + TypeScript
├── services/         # Microserviços (LPR, ONVIF, Recording, etc)
├── scripts/          # Scripts de automação e provisionamento
├── tests/            # Testes e validações
├── docs/             # Documentação técnica
├── config/           # Arquivos de configuração (mediamtx.yml, etc)
├── data/             # Dados de teste e payloads JSON
├── viewers/          # Visualizadores HTML (LPR, streams)
├── test-data/        # Vídeos e imagens para teste
├── recordings/       # Gravações de vídeo
├── snapshots/        # Snapshots de câmeras
├── haproxy/          # Configuração HAProxy
├── kong/             # Configuração Kong Gateway
├── nginx/            # Configuração Nginx
└── legacy/           # Código legado
```

## Quick Start

1. Configure as variáveis de ambiente:
   ```bash
   cp .env.example .env
   ```

2. Inicie os serviços:
   ```bash
   docker-compose up -d
   ```

3. Acesse:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - MediaMTX: rtsp://localhost:8554

## Documentação

- [Configuração para Máquina de IA](docs/CONFIGURACAO_MAQUINA_IA.md)
- [Arquitetura MVP](docs/mvp/INDEX.md)
- [Testes de Carga](docs/LOAD_TESTING.md)
- [Segurança](SECURITY.md)

## Scripts Úteis

- `scripts/provision_all.py` - Provisiona todas as câmeras
- `scripts/add_cameras.bat` - Adiciona câmeras ao sistema
- `scripts/load_test.py` - Testes de carga
- `tests/quick_test.bat` - Teste rápido do sistema
