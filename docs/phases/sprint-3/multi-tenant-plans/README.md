# Multi-Tenant + Planos - Sistema Completo

## 🎯 Visão Geral

Sistema multi-tenant com 3 níveis de permissão e planos diferenciados para controle de custos e monetização.

---

## 📚 Documentação Completa

1. **[WHAT.md](./WHAT.md)** - O que foi implementado
2. **[WHY.md](./WHY.md)** - Por que fizemos assim (alternativas e trade-offs)
3. **[IMPACT.md](./IMPACT.md)** - Impacto no negócio e métricas
4. **[METRICS.md](./METRICS.md)** - Fórmulas matemáticas (DAU, RPS, RPD, custos)
5. **[IMPORTANCE.md](./IMPORTANCE.md)** - Quando usar/não usar

---

## 🚀 Quick Start

### 1. Aplicar Migrations
```bash
docker-compose exec backend python manage.py migrate
```

### 2. Popular Dados de Teste
```bash
docker-compose exec backend python manage.py populate_tenants
```

**Cria:**
- Org: São Paulo (Plano Pro - 15 dias)
  - Email: admin@saopaulo.com
  - Senha: senha123
- Org: Rio de Janeiro (Plano Basic - 7 dias)
  - Email: admin@rio.com
  - Senha: senha123

### 3. Acessar Django Admin (Platform Admin)
```
URL: http://localhost:8000/admin
User: (criar superuser)
```

```bash
docker-compose exec backend python manage.py createsuperuser
```

### 4. Testar API
```bash
# Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@saopaulo.com","password":"senha123"}'

# Listar usuários da organização
curl -X GET http://localhost:8000/api/usuarios/ \
  -H "Authorization: Bearer <access_token>"

# Criar usuário (limite do plano)
curl -X POST http://localhost:8000/api/usuarios/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@saopaulo.com","name":"User SP","password":"senha123","role":"viewer"}'
```

---

## 🔐 Níveis de Permissão

### 1. Platform Admin (Superuser)
- Acessa Django Admin
- Gerencia Organizations e Subscriptions
- Não vê câmeras/gravações

### 2. Organization Admin
- Cria até 5 usuários (limite do plano)
- Gerencia câmeras
- Vê detecções e gravações

### 3. User (Viewer)
- Apenas visualiza câmeras
- Vê gravações
- Read-only

---

## 📊 Planos

| Plano | Gravação | Câmeras | Usuários | Clipes | Streams | Preço |
|-------|----------|---------|----------|--------|---------|-------|
| Basic | 7 dias | 10 | 3 | 10 | 4 | $117/mês |
| Pro | 15 dias | 50 | 5 | 50 | 16 | $1,137/mês |
| Premium | 30 dias | 200 | 10 | ∞ | 64 | $8,874/mês |

---

## 📡 API Endpoints

### Platform Admin (Django Admin)
```
/admin/tenants/organization/
/admin/tenants/subscription/
```

### Organizations (Platform Admin only)
```
GET    /api/organizations/
POST   /api/organizations/
GET    /api/organizations/{id}/
PUT    /api/organizations/{id}/
DELETE /api/organizations/{id}/
```

### Subscriptions (Platform Admin only)
```
GET    /api/subscriptions/
POST   /api/subscriptions/
GET    /api/subscriptions/{id}/
PUT    /api/subscriptions/{id}/
GET    /api/subscriptions/my_subscription/  # Org do usuário
```

### Users (Org Admin)
```
GET    /api/usuarios/               # Filtrado por org
POST   /api/usuarios/               # Limite do plano
GET    /api/usuarios/{id}/
PUT    /api/usuarios/{id}/
DELETE /api/usuarios/{id}/
```

---

## 🧪 Testes

### 1. Testar Isolamento de Dados
```bash
# Login como admin SP
TOKEN_SP=$(curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@saopaulo.com","password":"senha123"}' \
  | jq -r '.access')

# Listar usuários (deve ver apenas SP)
curl -X GET http://localhost:8000/api/usuarios/ \
  -H "Authorization: Bearer $TOKEN_SP"
```

### 2. Testar Limite de Usuários
```bash
# Criar 5 usuários (Pro permite 5)
for i in {1..6}; do
  curl -X POST http://localhost:8000/api/usuarios/ \
    -H "Authorization: Bearer $TOKEN_SP" \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"user$i@saopaulo.com\",\"name\":\"User $i\",\"password\":\"senha123\",\"role\":\"viewer\"}"
done

# 6º deve retornar 403 Forbidden
```

### 3. Testar Permissões
```bash
# Login como viewer
TOKEN_VIEWER=$(curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"user1@saopaulo.com","password":"senha123"}' \
  | jq -r '.access')

# Tentar criar usuário (deve falhar)
curl -X POST http://localhost:8000/api/usuarios/ \
  -H "Authorization: Bearer $TOKEN_VIEWER" \
  -H "Content-Type: application/json" \
  -d '{"email":"hacker@test.com","name":"Hacker","password":"senha123"}'

# Deve retornar 403 Forbidden
```

---

## 📊 Métricas

### DAU (Daily Active Users)
```
Basic: 2 DAU
Pro: 4 DAU
Premium: 8 DAU
```

### RPS (Requests Per Second)
```
Basic: 0.0022 RPS
Pro: 0.0044 RPS
Premium: 0.0089 RPS

100 orgs: ~1 RPS
```

### Storage
```
Basic: 1.5 TB
Pro: 16.2 TB
Premium: 129.6 TB
```

### Custos
```
Basic: $39/mês (custo) → $117/mês (preço)
Pro: $379/mês (custo) → $1,137/mês (preço)
Premium: $2,958/mês (custo) → $8,874/mês (preço)

Margem: 200% (3x custo)
```

Ver [METRICS.md](./METRICS.md) para fórmulas completas.

---

## ✅ Checklist de Implementação

```
[x] Models (Organization, Subscription)
[x] Middleware (TenantMiddleware)
[x] Permissions (3 níveis)
[x] API Endpoints
[x] Django Admin
[x] Migrations
[x] Dados de teste
[x] Documentação completa
[x] Fórmulas matemáticas
[x] Testes de isolamento
```

---

## 🔄 Próximos Passos

1. **Recording Service** - Usar `recording_days` do plano
2. **Sobrescrita Cíclica** - Deletar gravações antigas
3. **Dashboard de Uso** - Mostrar limites vs uso atual
4. **Billing System** - Integração com Stripe
5. **Transferência de Usuários** - Entre organizações

---

## 📁 Arquivos Criados

```
backend/apps/tenants/
├── models.py
├── serializers.py
├── views.py
├── urls.py
├── admin.py
├── permissions.py
├── middleware.py
└── management/commands/populate_tenants.py

docs/phases/sprint-3/multi-tenant-plans/
├── README.md (este arquivo)
├── WHAT.md
├── WHY.md
├── IMPACT.md
├── METRICS.md
└── IMPORTANCE.md
```

---

## 🎯 KPIs de Sucesso

```
✅ Isolamento: Admin não vê outras orgs
✅ Limites: Não pode exceder plano
✅ Performance: < 100ms por request
✅ Custo: Previsível por plano
✅ Onboarding: < 10 minutos
✅ Margem: 200% (3x custo)
```
