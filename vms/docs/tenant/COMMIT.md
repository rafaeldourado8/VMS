# Commit - PASSO 1

```bash
git add src/shared/admin/cidades/
git add src/config/
git add src/manage.py
git add src/.env
git add src/requirements.txt
git add src/docker/admin/
git add src/infrastructure/database/
git add src/infrastructure/test/passo1-tenant/
git add docker-compose.yml
git add docs/passo1-tenant/

git commit -m "feat: domínio tenant (City) com Django + PostgreSQL

PASSO 1 - Domínio mínimo de Tenant:
- Model City (UUID, name, status, plan)
- Enums: CityStatus, Plan
- Admin interface completa
- PostgreSQL + wait-for-db
- Migrations automáticas
- 7 testes unitários e integração

Regras:
- UUID como primary key
- Nome único por cidade
- Status padrão: ACTIVE
- Plano padrão: BASIC
- Base para isolamento multi-tenant

Stack:
- Django 5.0
- PostgreSQL 16
- Docker Compose

Testes: ✅ 7/7 passing

Refs: RULES.md PASSO 1"
```
