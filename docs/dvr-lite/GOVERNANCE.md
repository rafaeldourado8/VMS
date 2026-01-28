# 🏢 DVR-Lite - Governança e Multi-Tenant

## 🎯 Modelo de Negócio

### Estrutura
```
DVR-Lite (Nós)
├── Super Admin (Governança)
├── Organização A (Cliente 1)
│   ├── Admin
│   ├── 50 câmeras
│   └── 100 sub-usuários
├── Organização B (Cliente 2)
│   ├── Admin
│   ├── 50 câmeras
│   └── 100 sub-usuários
└── Organização N (Cliente N)
```

---

## 👤 Níveis de Acesso

### 1. Super Admin (Nós - DVR-Lite)
**Quem:** Equipe técnica/comercial da DVR-Lite

**Acesso:**
- ✅ Todas as organizações (clientes)
- ✅ Todas as VPS
- ✅ Métricas globais
- ✅ Logs de auditoria

**Permissões:**
- ✅ Criar/editar/deletar organizações
- ✅ Criar admin de organização
- ✅ Ver uso de recursos (CPU, RAM, disco, banda)
- ✅ Gerenciar billing e planos
- ✅ Suporte técnico (acesso temporário)
- ✅ Configurar limites (câmeras, usuários, storage)
- ✅ Exportar relatórios globais

**Dashboard:**
```
┌─────────────────────────────────────────────────────────┐
│  Super Admin Dashboard                                  │
├─────────────────────────────────────────────────────────┤
│  Total Organizações: 10                                 │
│  Total Câmeras: 500                                     │
│  Total Usuários: 1,000                                  │
│  Storage Usado: 50 TB / 100 TB                          │
│  Banda Mensal: 15 TB / 50 TB                            │
│                                                         │
│  Organizações:                                          │
│  ├─ Empresa A (50 cams, 100 users) - $88/mês           │
│  ├─ Empresa B (30 cams, 50 users)  - $60/mês           │
│  └─ Empresa C (20 cams, 30 users)  - $45/mês           │
└─────────────────────────────────────────────────────────┘
```

---

### 2. Admin Organização (Cliente)
**Quem:** Dono/gerente da empresa cliente

**Acesso:**
- ✅ Apenas sua organização
- ✅ Todas as câmeras da organização (até 50)
- ✅ Todos os sub-usuários (até 100)
- ❌ Outras organizações

**Permissões:**
- ✅ Criar/editar/deletar câmeras
- ✅ Criar/editar/deletar sub-usuários
- ✅ Atribuir câmeras a sub-usuários
- ✅ Ver todos os clipes da organização
- ✅ Ver relatórios de uso
- ✅ Configurar retenção de gravações
- ❌ Alterar limites de plano
- ❌ Ver outras organizações

**Dashboard:**
```
┌─────────────────────────────────────────────────────────┐
│  Empresa A - Admin Dashboard                            │
├─────────────────────────────────────────────────────────┤
│  Câmeras: 45/50                                         │
│  Usuários: 80/100                                       │
│  Storage: 3.5 TB / 5 TB                                 │
│  Plano: Professional ($88/mês)                          │
│                                                         │
│  Câmeras Ativas: 45                                     │
│  Usuários Online: 12                                    │
│  Gravações: 7 dias                                      │
│  Clipes Criados: 234                                    │
└─────────────────────────────────────────────────────────┘
```

---

### 3. Sub-Usuário (Operador)
**Quem:** Funcionário/operador do cliente

**Acesso:**
- ✅ Apenas 1 câmera atribuída
- ❌ Outras câmeras
- ❌ Outras organizações

**Permissões:**
- ✅ Ver streaming ao vivo
- ✅ Ver gravações (7 dias)
- ✅ Criar clipes (máx 5min)
- ✅ Download de clipes
- ❌ Criar/editar câmeras
- ❌ Ver outras câmeras
- ❌ Criar usuários

**Dashboard:**
```
┌─────────────────────────────────────────────────────────┐
│  João Silva - Operador                                  │
├─────────────────────────────────────────────────────────┤
│  Câmera Atribuída: Portaria Principal                   │
│  Status: Online                                         │
│                                                         │
│  [Ver Ao Vivo] [Gravações] [Criar Clipe]               │
│                                                         │
│  Meus Clipes: 12                                        │
│  Último acesso: Hoje às 14:30                           │
└─────────────────────────────────────────────────────────┘
```

---

## 🔐 Isolamento Multi-Tenant

### Banco de Dados
```sql
-- Todas as queries filtram por org_id
SELECT * FROM cameras WHERE org_id = :current_org_id;
SELECT * FROM users WHERE org_id = :current_org_id;
SELECT * FROM recordings WHERE camera_id IN (
  SELECT id FROM cameras WHERE org_id = :current_org_id
);
```

### Storage
```
/recordings/
├── org-1-empresa-a/
│   ├── camera-1/
│   ├── camera-2/
│   └── ...
├── org-2-empresa-b/
│   ├── camera-1/
│   └── ...
└── org-3-empresa-c/
```

### API
```
# Middleware automático
X-Organization-ID: 1

# Todas as rotas filtram por organização
GET /api/cameras/          → Apenas câmeras da org 1
GET /api/users/            → Apenas usuários da org 1
GET /api/recordings/       → Apenas gravações da org 1
```

---

## 🛡️ Segurança

### Autenticação
```
JWT Token contém:
{
  "user_id": 123,
  "org_id": 1,
  "role": "org_admin",
  "permissions": ["view_cameras", "create_users"]
}
```

### Autorização
```python
# Middleware de permissões
def check_organization_access(user, resource):
    if user.role == "super_admin":
        return True  # Acesso total
    
    if user.role == "org_admin":
        return resource.org_id == user.org_id
    
    if user.role == "sub_user":
        return resource.id in user.allowed_camera_ids
```

### Auditoria
```sql
-- Tabela de logs
CREATE TABLE audit_logs (
  id SERIAL PRIMARY KEY,
  user_id INT,
  org_id INT,
  action VARCHAR(50),  -- 'view_camera', 'create_clip', etc
  resource_type VARCHAR(50),
  resource_id INT,
  ip_address VARCHAR(45),
  timestamp TIMESTAMP DEFAULT NOW()
);
```

---

## 📊 Métricas por Organização

### Super Admin vê:
```
Organização A:
- Câmeras: 45/50
- Usuários: 80/100
- Storage: 3.5 TB / 5 TB
- Banda: 2 TB / 10 TB
- Uptime: 99.8%
- Custo: $88/mês

Organização B:
- Câmeras: 30/50
- Usuários: 50/100
- Storage: 2.1 TB / 5 TB
- Banda: 1.5 TB / 10 TB
- Uptime: 99.9%
- Custo: $60/mês
```

### Admin Organização vê:
```
Minha Organização:
- Câmeras ativas: 45
- Usuários online: 12
- Storage usado: 3.5 TB
- Gravações: 7 dias
- Clipes: 234
- Alertas: 3
```

---

## 💰 Billing e Planos

### Planos por Organização
```
Basic:
- 20 câmeras
- 50 usuários
- 7 dias gravação
- 2 TB storage
- $45/mês

Professional:
- 50 câmeras
- 100 usuários
- 7 dias gravação
- 5 TB storage
- $88/mês

Enterprise:
- 100 câmeras
- 200 usuários
- 15 dias gravação
- 10 TB storage
- $150/mês
```

### Cobrança
```
Super Admin gerencia:
- Plano de cada organização
- Upgrades/downgrades
- Faturamento mensal
- Histórico de pagamentos
- Suspensão por inadimplência
```

---

## 🔧 Configuração Multi-Tenant

### Variáveis de Ambiente
```bash
# Multi-tenant
MULTI_TENANT_ENABLED=true
DEFAULT_ORG_MAX_CAMERAS=50
DEFAULT_ORG_MAX_USERS=100
DEFAULT_ORG_STORAGE_GB=5000

# Super Admin
SUPER_ADMIN_EMAIL=admin@dvrlite.com
SUPER_ADMIN_PASSWORD=secure_password
```

### Criação de Organização
```bash
# Via Super Admin Dashboard
POST /api/admin/organizations/
{
  "name": "Empresa A",
  "slug": "empresa-a",
  "max_cameras": 50,
  "max_users": 100,
  "max_storage_gb": 5000,
  "plan": "professional",
  "admin_email": "admin@empresaa.com",
  "admin_password": "temp_password"
}
```

---

## 📋 Fluxo de Onboarding

### 1. Super Admin cria organização
```
1. Acessa Super Admin Dashboard
2. Clica em "Nova Organização"
3. Preenche dados:
   - Nome: Empresa A
   - Plano: Professional
   - Email admin: admin@empresaa.com
4. Sistema cria:
   - Organização no banco
   - Admin da organização
   - Envia email com credenciais
```

### 2. Admin Organização configura
```
1. Recebe email com credenciais
2. Faz primeiro login
3. Adiciona câmeras (até 50)
4. Cria sub-usuários (até 100)
5. Atribui câmeras aos usuários
```

### 3. Sub-usuário acessa
```
1. Recebe credenciais do admin
2. Faz login
3. Vê apenas sua câmera
4. Pode criar clipes
```

---

## 🎯 Resumo

```
┌─────────────────────────────────────────────────────────┐
│                  Governança DVR-Lite                    │
├─────────────────────────────────────────────────────────┤
│  Nível 1: Super Admin (Nós)                             │
│    ├─ Acesso: Todas organizações                        │
│    ├─ Gerencia: Billing, planos, suporte               │
│    └─ Dashboard: Métricas globais                       │
│                                                         │
│  Nível 2: Admin Organização (Cliente)                   │
│    ├─ Acesso: Sua organização                           │
│    ├─ Gerencia: Câmeras, usuários                       │
│    └─ Dashboard: Métricas da organização                │
│                                                         │
│  Nível 3: Sub-Usuário (Operador)                        │
│    ├─ Acesso: 1 câmera                                  │
│    ├─ Gerencia: Clipes próprios                         │
│    └─ Dashboard: Visualização simples                   │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 Próximos Passos

Ver [CHECKLIST.md](CHECKLIST.md) Sprint 4 para implementação de:
- Multi-tenant database
- Super Admin dashboard
- Organization management
- Billing system
- Audit logs
