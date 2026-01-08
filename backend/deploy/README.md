# 🚀 Deploy VMS Backend

## Arquivos de Deploy

### Docker
- `Dockerfile` - Imagem Docker otimizada para produção
- `docker-compose.staging.yml` - Configuração para ambiente de staging
- `entrypoint.sh` - Script de inicialização do container

### Scripts
- `deploy_staging.bat` - Script automatizado de deploy para staging (Windows)

## Deploy Rápido - Staging

### Windows
```bash
deploy_staging.bat
```

### Manual
```bash
docker-compose -f docker-compose.staging.yml up -d --build
```

## Estrutura dos Serviços

- **backend** - API Django + Gunicorn
- **db** - PostgreSQL 15
- **redis** - Redis 7 (cache e broker)
- **celery** - Worker para tarefas assíncronas

## Portas

- Backend: 8000
- PostgreSQL: 5432
- Redis: 6379

## Documentação Completa

Veja `docs/DEPLOY.md` para instruções detalhadas de deploy em staging e produção.