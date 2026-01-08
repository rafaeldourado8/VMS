# 🎯 VMS Backend - Arquitetura DDD

Sistema de monitoramento de câmeras com IA, refatorado seguindo Domain-Driven Design.

## 📊 Status: 98% Completo (55/56 tarefas)

## 🏗️ Estrutura do Projeto

```
backend/
├── domain/              # Camada de Domínio (Regras de Negócio)
├── application/         # Camada de Aplicação (Use Cases)
├── infrastructure/      # Camada de Infraestrutura (Implementações)
├── apps/               # Django Apps (Presentation Layer)
├── config/             # Configurações Django
├── tests/              # Testes automatizados
├── docs/               # 📚 Documentação
├── scripts/            # 🔧 Scripts utilitários
├── deploy/             # 🚀 Arquivos de deploy
├── logs/               # Logs da aplicação
└── migrations/         # Migrações customizadas
```

## 🚀 Quick Start

### Desenvolvimento Local
```bash
python manage.py runserver
```

### Staging
```bash
cd deploy
deploy_staging.bat
```

### Testes
```bash
pytest
python scripts/test_e2e_staging.py
```

## 📚 Documentação

- [Checklist de Refatoração](docs/CHECKLIST_REFATORACAO.md)
- [Arquitetura DDD](docs/ARQUITETURA_ATUAL.md)
- [Guia de Deploy](docs/DEPLOY.md)
- [Resumo Completo](docs/REFATORACAO_COMPLETA.md)

## 🔧 Scripts Úteis

```bash
# Organizar imports
python scripts/organize_imports.py

# Otimizar índices do banco
python scripts/optimize_indexes.py

# Testes E2E
python scripts/test_e2e_staging.py
```

## 🎯 Contextos DDD Implementados

1. ✅ **Monitoring** - Gerenciamento de câmeras
2. ✅ **Detection** - Detecções de IA
3. ✅ **User** - Usuários e autenticação
4. ✅ **Configuration** - Configurações globais
5. ✅ **Analytics** - Dashboard e métricas
6. ✅ **Support** - Mensagens de suporte
7. ✅ **Clips** - Clips de vídeo

## 🛠️ Tecnologias

- Django 5.2.7
- Django REST Framework 3.16.1
- PostgreSQL 15
- Redis 7
- Celery 5.3.4
- Docker & Docker Compose

## 📦 Dependências

```bash
pip install -r requirements.txt
```

## 🔍 Health Check

```bash
curl http://localhost:8000/health/
```

## 📝 Licença

Proprietary - VMS Project