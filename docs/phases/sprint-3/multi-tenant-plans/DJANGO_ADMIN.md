# 🔐 Django Admin - Platform Admin

## 🎯 Acesso

**URL:** http://localhost:8000/admin

**Título:** VMS Platform Admin

---

## 👤 Criar Superuser (Platform Admin)

```bash
docker-compose exec backend python manage.py createsuperuser
```

**Preencher:**
- Email: platform@admin.com
- Name: Platform Admin
- Password: (sua senha segura)

---

## 📊 O Que Você Pode Gerenciar

### 1. Organizations (Tenants)
**Path:** `/admin/tenants/organization/`

**Campos:**
- Name: Nome da cidade/empresa
- Slug: Identificador único (ex: sao-paulo)
- Database name: Nome do banco (ex: vms_sao_paulo)
- Is active: Status

**Ações:**
- ✅ Criar nova organização
- ✅ Editar organização
- ✅ Desativar organização
- ✅ Ver quantidade de usuários

---

### 2. Subscriptions (Planos)
**Path:** `/admin/tenants/subscription/`

**Campos:**
- Organization: Selecionar organização
- Plan: basic/pro/premium
- Is active: Status
- Expires at: Data de expiração (opcional)

**Limites (Auto-calculados):**
- Recording days: 7/15/30
- Max cameras: 10/50/200
- Max users: 3/5/10
- Max clips: 10/50/ilimitado
- Max concurrent streams: 4/16/64

**Ações:**
- ✅ Criar plano para organização
- ✅ Upgrade/downgrade de plano
- ✅ Ativar/desativar plano
- ✅ Ver limites calculados

---

### 3. Users (Usuários)
**Path:** `/admin/usuarios/usuario/`

**Campos:**
- Email
- Name
- Organization: Vincular a organização
- Role: admin/viewer
- Plan: basic/pro/premium
- Is active: Status
- Is staff: Acesso ao admin
- Is superuser: Platform Admin

**Filtros:**
- Por organização
- Por role
- Por plano
- Por status

**Ações:**
- ✅ Criar usuário para organização
- ✅ Transferir usuário entre organizações
- ✅ Promover para admin
- ✅ Desativar usuário

---

## 🔐 Permissões

### Platform Admin (Superuser)
- ✅ Vê TODAS as organizações
- ✅ Vê TODOS os usuários
- ✅ Cria/edita/deleta tudo
- ❌ NÃO vê câmeras/gravações (use API)

### Organization Admin (is_staff=True)
- ✅ Vê apenas SUA organização
- ✅ Vê apenas usuários da SUA organização
- ⚠️ Pode editar usuários da sua org
- ❌ NÃO vê outras organizações

---

## 📋 Workflow de Onboarding

### 1. Criar Organização
```
Admin → Tenants → Organizations → Add
- Name: São Paulo
- Slug: sao-paulo
- Database name: vms_sao_paulo
- Is active: ✓
```

### 2. Criar Subscription
```
Admin → Tenants → Subscriptions → Add
- Organization: São Paulo
- Plan: pro
- Is active: ✓
```

**Limites são calculados automaticamente!**

### 3. Criar Admin da Organização
```
Admin → Usuarios → Add
- Email: admin@saopaulo.com
- Name: Admin SP
- Organization: São Paulo
- Role: admin
- Plan: pro (herdado da org)
- Is active: ✓
- Is staff: ✓ (se quiser acesso ao admin)
```

### 4. Admin da Org Cria Usuários
**Via API (não pelo admin):**
```bash
curl -X POST http://localhost:8000/api/usuarios/ \
  -H "Authorization: Bearer <token>" \
  -d '{"email":"user@saopaulo.com","name":"User","role":"viewer"}'
```

---

## 🎨 Customizações Implementadas

### Títulos
- Site header: "VMS Platform Admin"
- Site title: "VMS Admin"
- Index title: "Gerenciamento de Organizações e Planos"

### Organization Admin
- Lista: name, slug, database_name, is_active, user_count, created_at
- Filtros: is_active, created_at
- Busca: name, slug
- Extra: Contador de usuários

### Subscription Admin
- Lista: organization, plan, recording_days, max_cameras, max_users, is_active, started_at
- Filtros: plan, is_active, started_at
- Busca: organization__name
- Fieldsets: Organização, Limites (colapsado), Datas
- Read-only: Todos os limites (auto-calculados)

### Usuario Admin
- Lista: email, name, organization, role, plan, is_active, is_staff, created_at
- Filtros: role, plan, is_active, is_staff, organization
- Busca: email, name, organization__name
- Fieldsets: Informações Básicas, Organização, Permissões, Datas
- Filtro automático: Org Admin só vê sua org

---

## 🧪 Testes

### 1. Acessar Admin
```
URL: http://localhost:8000/admin
Login: platform@admin.com
```

### 2. Verificar Organizações
```
Admin → Tenants → Organizations
Deve ver: São Paulo, Rio de Janeiro
```

### 3. Verificar Planos
```
Admin → Tenants → Subscriptions
Deve ver:
- São Paulo: Pro (15 dias)
- Rio de Janeiro: Basic (7 dias)
```

### 4. Verificar Usuários
```
Admin → Usuarios
Deve ver:
- admin@saopaulo.com (São Paulo)
- admin@rio.com (Rio de Janeiro)
```

### 5. Criar Nova Organização
```
Add Organization:
- Name: Belo Horizonte
- Slug: belo-horizonte
- Database name: vms_belo_horizonte

Add Subscription:
- Organization: Belo Horizonte
- Plan: premium

Verificar limites:
- Recording days: 30 ✓
- Max cameras: 200 ✓
- Max users: 10 ✓
```

---

## 📊 Dashboard do Admin

### Visão Geral
```
Organizations: 2
Subscriptions: 2
Users: 3

Recent Actions:
- Created organization "São Paulo"
- Created subscription for "São Paulo"
- Created user "admin@saopaulo.com"
```

---

## 🔒 Segurança

### Proteções Implementadas
1. ✅ CSRF desabilitado apenas para login (dev)
2. ✅ Org Admin só vê sua organização
3. ✅ Limites read-only (não podem ser editados manualmente)
4. ✅ Filtros automáticos por organização

### Recomendações
1. ⚠️ Use HTTPS em produção
2. ⚠️ Habilite CSRF em produção
3. ⚠️ Use senhas fortes para superusers
4. ⚠️ Limite acesso ao admin por IP (firewall)

---

## 📁 Arquivos Modificados

```
backend/config/urls.py
  + Customização de títulos

backend/config/settings.py
  + ADMIN_SITE_HEADER
  + ADMIN_SITE_TITLE
  + ADMIN_INDEX_TITLE

backend/apps/tenants/admin.py
  + OrganizationAdmin melhorado
  + SubscriptionAdmin com fieldsets

backend/apps/usuarios/admin.py
  + UsuarioAdmin com filtro por org
  + Fieldsets organizados
```

---

## 🎯 Próximos Passos

### Opcional: Frontend Customizado
Se quiser criar um frontend React para Platform Admin:

```
frontend/src/pages/platform/
├── Organizations.tsx
├── Subscriptions.tsx
└── Users.tsx
```

**Mas o Django Admin já fornece:**
- ✅ CRUD completo
- ✅ Filtros e busca
- ✅ Validações
- ✅ Histórico de mudanças
- ✅ Permissões granulares

**Recomendação:** Use Django Admin por enquanto, crie frontend customizado apenas se necessário.
