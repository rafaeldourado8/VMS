# Multi-Tenant + Planos - O QUE FOI FEITO

## 📋 Resumo

Sistema multi-tenant com gerenciamento de planos e permissões em 3 níveis hierárquicos.

---

## 🏗️ Componentes Implementados

### 1. Models

#### Organization
```python
- name: Nome da cidade/empresa
- slug: Identificador único
- database_name: Nome do banco (futuro)
- is_active: Status
- created_at: Data de criação
```

#### Subscription
```python
- organization: FK para Organization
- plan: basic/pro/premium
- recording_days: 7/15/30 dias
- max_cameras: 10/50/200
- max_users: 3/5/10
- max_clips: 10/50/ilimitado
- max_concurrent_streams: 4/16/64
- is_active: Status
- started_at: Início
- expires_at: Expiração
```

#### Usuario (atualizado)
```python
+ organization: FK para Organization
+ Propriedades dinâmicas baseadas no plano da org
```

---

## 🔐 Sistema de Permissões (3 Níveis)

### 1. Platform Admin (Superuser)
- **Acesso:** Django Admin completo
- **Pode:**
  - Criar/editar/deletar Organizations
  - Gerenciar Subscriptions
  - Ver todas as organizações
  - Não vê câmeras/gravações

### 2. Organization Admin
- **Acesso:** API do sistema
- **Pode:**
  - Criar até 5 usuários (limite do plano)
  - Gerenciar câmeras da organização
  - Ver detecções e gravações
  - Transferir usuários entre organizações (futuro)

### 3. User (Viewer)
- **Acesso:** API do sistema (read-only)
- **Pode:**
  - Ver câmeras da organização
  - Ver gravações
  - Ver detecções
  - Não pode criar/editar/deletar

---

## 📊 Planos Implementados

| Plano | Gravação | Câmeras | Usuários | Clipes | Streams |
|-------|----------|---------|----------|--------|---------|
| Basic | 7 dias | 10 | 3 | 10 | 4 |
| Pro | 15 dias | 50 | 5 | 50 | 16 |
| Premium | 30 dias | 200 | 10 | ∞ | 64 |

---

## 🔧 Middleware

**TenantMiddleware:**
- Detecta organização do usuário autenticado
- Injeta `request.tenant` em todas as requisições
- Base para futuro roteamento de banco

---

## 📡 API Endpoints

### Platform Admin (Django Admin)
```
/admin/tenants/organization/
/admin/tenants/subscription/
```

### Organization Management
```
GET    /api/organizations/          # Listar
POST   /api/organizations/          # Criar
GET    /api/organizations/{id}/     # Detalhe
PUT    /api/organizations/{id}/     # Atualizar
DELETE /api/organizations/{id}/     # Deletar

GET    /api/subscriptions/          # Listar
POST   /api/subscriptions/          # Criar
GET    /api/subscriptions/{id}/     # Detalhe
PUT    /api/subscriptions/{id}/     # Atualizar
```

### User Management (Admin)
```
GET    /api/usuarios/               # Listar (filtrado por org)
POST   /api/usuarios/               # Criar (limite do plano)
GET    /api/usuarios/{id}/          # Detalhe
PUT    /api/usuarios/{id}/          # Atualizar
DELETE /api/usuarios/{id}/          # Deletar
```

---

## 🧪 Dados de Teste

**Comando:**
```bash
docker-compose exec backend python manage.py populate_tenants
```

**Cria:**
- Org: São Paulo (Plano Pro - 15 dias)
  - admin@saopaulo.com / senha123
- Org: Rio de Janeiro (Plano Basic - 7 dias)
  - admin@rio.com / senha123

---

## ✅ Validações Implementadas

1. **Limite de usuários:** Admin não pode criar mais que o limite do plano
2. **Filtro por organização:** Admin só vê usuários da sua org
3. **Herança de organização:** Novos usuários herdam org do admin
4. **Permissões hierárquicas:** Platform > Org Admin > User
5. **Auto-set de limites:** Subscription define limites automaticamente

---

## 📁 Arquivos Criados

```
backend/apps/tenants/
├── __init__.py
├── apps.py
├── models.py              # Organization, Subscription
├── serializers.py         # API serializers
├── views.py               # ViewSets
├── urls.py                # Rotas
├── admin.py               # Django Admin
├── permissions.py         # Permissões customizadas
├── middleware.py          # TenantMiddleware
└── management/
    └── commands/
        └── populate_tenants.py

backend/apps/usuarios/
├── models.py              # + organization FK
└── views.py               # + limite de usuários
```

---

## 🔄 Migrations

```
tenants.0001_initial
  - Create Organization
  - Create Subscription

usuarios.0004_usuario_organization
  - Add organization FK
```
