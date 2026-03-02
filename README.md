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
   # Edite o .env com suas credenciais
   ```

2. Inicie os serviços:
   ```bash
   docker-compose up -d
   ```

3. Configure replicação PostgreSQL:
   ```bash
   # Windows
   scripts\init_postgres_replication.bat
   
   # Linux/Mac
   bash scripts/init_postgres_replication.sh
   ```

4. Acesse:
   - Frontend: http://localhost/
   - Backend API: http://localhost/api/
   - Admin Django: http://localhost/admin/
   - HAProxy Stats: http://localhost:8404/stats
   - MediaMTX RTSP: rtsp://localhost:8554

## Documentação

- [Mudanças de Arquitetura](docs/ARCHITECTURE_CHANGES.md) ⭐ NOVO
- [Sistema de Fallback para Streaming](docs/STREAMING_FALLBACK.md) ⭐ NOVO
- [Frontend Connection Refused - Solução](docs/FRONTEND_CONNECTION_REFUSED.md) ⭐ NOVO
- [Configuração para Máquina de IA](docs/CONFIGURACAO_MAQUINA_IA.md)
- [Arquitetura MVP](docs/mvp/INDEX.md)
- [Testes de Carga](docs/LOAD_TESTING.md)
- [Segurança](SECURITY.md)

## Scripts Úteis

- `scripts/fix_frontend.bat` - Corrige problema de Connection Refused do frontend ⭐ NOVO
- `scripts/monitor_frontend.bat` - Monitora e reinicia frontend automaticamente ⭐ NOVO
- `scripts/init_postgres_replication.bat` - Configura replicação PostgreSQL (Windows)
- `scripts/init_postgres_replication.sh` - Configura replicação PostgreSQL (Linux/Mac)
- `scripts/provision_all.py` - Provisiona todas as câmeras
- `scripts/add_cameras.bat` - Adiciona câmeras ao sistema
- `scripts/load_test.py` - Testes de carga
- `tests/quick_test.bat` - Teste rápido do sistema

## Arquitetura

### Gateway Unificado
- **HAProxy** como ponto único de entrada (porta 80)
- Kong Gateway acessível via HAProxy
- Roteamento inteligente para todos os serviços

### Banco de Dados
- **PostgreSQL Primary** (write operations)
- **PostgreSQL Replica 1** (read operations)
- **PostgreSQL Replica 2** (read operations)
- Replicação streaming assíncrona


## Deploy e CI/CD

- [Guia EC2 Spot + CI/CD](docs/AWS_EC2_SPOT_SETUP.md) ⭐ NOVO - Setup completo para desenvolvimento
- [Checklist de Deploy](docs/DEPLOY_CHECKLIST.md) ⭐ NOVO - Passo a passo rápido
