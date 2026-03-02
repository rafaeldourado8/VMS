# VMS - Video Management System

Sistema de gerenciamento de vídeo com detecção de placas (LPR) e streaming RTSP.

## 🚨 Code Review Completo Realizado

**⭐ NOVO:** Foi realizado um code review completo do projeto identificando 30+ problemas.

**Acesse:** [docs/code-review/INDEX.md](docs/code-review/INDEX.md)

**Prioridades:**
- 🔴 **P0 - Crítico:** Credenciais hardcoded, DEBUG=True, SQL Injection
- 🟠 **P1 - Alto:** Rate limiting, CORS, validação de inputs
- 🟡 **P2 - Médio:** Código duplicado, queries N+1, testes

**Consulte o Code Issues Panel no IDE para ver todos os findings detalhados.**

---

## Estrutura do Projeto

```
VMS/
├── backend/          # Django API
├── frontend/         # React + TypeScript
├── services/         # Microserviços (LPR, ONVIF, Recording, etc)
├── scripts/          # Scripts de automação e provisionamento
├── tests/            # Testes e validações
├── docs/             # Documentação técnica
│   └── code-review/  # ⭐ NOVO - Resultados do code review
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

### Code Review & Qualidade (NOVO)
- [Índice do Code Review](docs/code-review/INDEX.md) ⭐ NOVO
- [Vulnerabilidades de Segurança](docs/code-review/SECURITY_ISSUES.md) ⭐ NOVO
- [Problemas de Qualidade](docs/code-review/CODE_QUALITY.md) ⭐ NOVO
- [Problemas de Infraestrutura](docs/code-review/INFRASTRUCTURE.md) ⭐ NOVO
- [Problemas de Performance](docs/code-review/PERFORMANCE.md) ⭐ NOVO
- [Riscos de Deployment](docs/code-review/DEPLOYMENT.md) ⭐ NOVO

### Guias de Correção (NOVO)
- [Como Corrigir SQL Injection](docs/code-review/guides/FIX_SQL_INJECTION.md) ⭐ NOVO
- [Como Remover Secrets](docs/code-review/guides/FIX_SECRETS.md) ⭐ NOVO
- [Como Configurar CORS](docs/code-review/guides/FIX_CORS.md) ⭐ NOVO
- [Como Implementar Rate Limiting](docs/code-review/guides/FIX_RATE_LIMITING.md) ⭐ NOVO
- [Como Otimizar Queries](docs/code-review/guides/FIX_QUERIES.md) ⭐ NOVO

### Arquitetura & Sistema
- [Organização da Documentação](docs/DOC_ORGANIZATION.md) ⭐ NOVO
- [Mudanças de Arquitetura](docs/ARCHITECTURE_CHANGES.md)
- [Sistema de Fallback para Streaming](docs/STREAMING_FALLBACK.md)
- [Frontend Connection Refused - Solução](docs/FRONTEND_CONNECTION_REFUSED.md)
- [Configuração para Máquina de IA](docs/CONFIGURACAO_MAQUINA_IA.md)
- [Arquitetura MVP](docs/mvp/INDEX.md)
- [Testes de Carga](docs/LOAD_TESTING.md)
- [Segurança](SECURITY.md)

### Deploy & DevOps
- [Guia EC2 Spot + CI/CD](docs/AWS_EC2_SPOT_SETUP.md)
- [Checklist de Deploy](docs/DEPLOY_CHECKLIST.md)

## Scripts Úteis

- `scripts/fix_frontend.bat` - Corrige problema de Connection Refused do frontend
- `scripts/monitor_frontend.bat` - Monitora e reinicia frontend automaticamente
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

## 🔒 Segurança

**IMPORTANTE:** Foram identificados problemas críticos de segurança no code review:
- Credenciais hardcoded no código
- DEBUG=True em configurações
- SQL Injection vulnerabilities
- CORS mal configurado
- Falta de rate limiting

**Ação Requerida:** Consulte [docs/code-review/SECURITY_ISSUES.md](docs/code-review/SECURITY_ISSUES.md)

## 📊 Qualidade de Código

**Status Atual:**
- Duplicação de código: Alta (>15%)
- Complexidade ciclomática: Média-Alta
- Cobertura de testes: Baixa (<50%)
- Type hints: Inconsistente

**Ação Requerida:** Consulte [docs/code-review/CODE_QUALITY.md](docs/code-review/CODE_QUALITY.md)

## 🚀 Próximos Passos

1. ✅ Code review completo realizado
2. ⏳ Corrigir problemas P0 (Críticos)
3. ⏳ Corrigir problemas P1 (Altos)
4. ⏳ Implementar testes automatizados
5. ⏳ Melhorar cobertura de testes
6. ⏳ Refatorar código duplicado

## Deploy e CI/CD

- [Guia EC2 Spot + CI/CD](docs/AWS_EC2_SPOT_SETUP.md) - Setup completo para desenvolvimento
- [Checklist de Deploy](docs/DEPLOY_CHECKLIST.md) - Passo a passo rápido
