# Multi-Tenant + Planos - POR QUE FIZEMOS ASSIM

## 🎯 Problema a Resolver

1. **Isolamento de dados** entre cidades/empresas
2. **Monetização** com planos diferenciados
3. **Controle de custos** baseado em uso
4. **Escalabilidade** para múltiplas organizações
5. **Permissões granulares** (Platform, Admin, User)

---

## 🔍 Alternativas Consideradas

### 1. Single-Tenant (Rejeitada)
**Como funciona:**
- 1 instância completa por cliente
- Banco, backend, frontend isolados

**Prós:**
- Isolamento total
- Customização por cliente

**Contras:**
- ❌ Custo alto ($500/cliente/mês)
- ❌ Manutenção complexa
- ❌ Não escala

**Por que rejeitamos:**
Inviável economicamente para pequenas cidades.

---

### 2. Multi-Tenant com Schema Separation (Considerada)
**Como funciona:**
- 1 banco, múltiplos schemas
- Cada org tem seu schema

**Prós:**
- Isolamento lógico
- Backup por schema

**Contras:**
- ⚠️ Complexidade de migrations
- ⚠️ Limite de schemas no PostgreSQL
- ⚠️ Performance degrada com muitos schemas

**Por que não escolhemos agora:**
Complexidade desnecessária para MVP. Pode ser implementado depois.

---

### 3. Multi-Tenant com Row-Level Security (ESCOLHIDA)
**Como funciona:**
- 1 banco compartilhado
- Filtro por `organization_id` em todas as queries
- Middleware injeta tenant no request

**Prós:**
- ✅ Simples de implementar
- ✅ Migrations unificadas
- ✅ Custo baixo
- ✅ Escala bem até 1000 orgs

**Contras:**
- ⚠️ Risco de vazamento de dados (se mal implementado)
- ⚠️ Backup é global (não por org)

**Por que escolhemos:**
- Melhor custo-benefício para MVP
- Fácil de migrar para schemas depois
- Django ORM facilita filtros automáticos

---

## 🏗️ Decisões de Arquitetura

### 1. Por que 3 Níveis de Permissão?

**Platform Admin (Superuser):**
- Gerencia o negócio (SaaS)
- Cria organizações e planos
- Não precisa ver câmeras

**Organization Admin:**
- Gerencia sua cidade/empresa
- Cria usuários (limite do plano)
- Controla câmeras e gravações

**User (Viewer):**
- Operador de monitoramento
- Apenas visualiza
- Não pode alterar nada

**Alternativa rejeitada:** 2 níveis (Admin + User)
- ❌ Admin teria que gerenciar planos (confuso)
- ❌ Mistura responsabilidades

---

### 2. Por que Limites no Plano da Organização?

**Decisão:** Limites em `Subscription`, não em `Usuario`

**Motivo:**
- ✅ Centralizado (1 fonte de verdade)
- ✅ Fácil de atualizar plano
- ✅ Usuário herda limites da org

**Alternativa rejeitada:** Limites no `Usuario`
- ❌ Duplicação de dados
- ❌ Inconsistência ao mudar plano
- ❌ Difícil de auditar

---

### 3. Por que Middleware para Tenant?

**Decisão:** `TenantMiddleware` injeta `request.tenant`

**Motivo:**
- ✅ Disponível em todas as views
- ✅ Não precisa passar `org_id` manualmente
- ✅ Base para futuro roteamento de banco

**Alternativa rejeitada:** Passar `org_id` em cada request
- ❌ Verboso
- ❌ Fácil de esquecer
- ❌ Risco de segurança

---

### 4. Por que Auto-Set de Limites no Subscription?

**Decisão:** `save()` override define limites automaticamente

```python
def save(self, *args, **kwargs):
    limits = {
        'basic': {'recording_days': 7, ...},
        'pro': {'recording_days': 15, ...},
        'premium': {'recording_days': 30, ...},
    }
    for key, value in limits[self.plan].items():
        setattr(self, key, value)
    super().save()
```

**Motivo:**
- ✅ Consistência garantida
- ✅ Não precisa lembrar de setar manualmente
- ✅ Fácil de mudar limites globalmente

**Alternativa rejeitada:** Setar manualmente
- ❌ Erro humano
- ❌ Inconsistência

---

### 5. Por que Limite de 5 Usuários para Admin?

**Decisão:** Admin pode criar até `max_users` do plano

**Motivo:**
- ✅ Monetização (upgrade para mais usuários)
- ✅ Controle de custos (menos DAU)
- ✅ Incentiva planos maiores

**Cálculo:**
```
Basic: 3 usuários × $117 = $39/usuário
Pro: 5 usuários × $1,137 = $227/usuário
Premium: 10 usuários × $8,874 = $887/usuário
```

**Alternativa rejeitada:** Usuários ilimitados
- ❌ Sem controle de custos
- ❌ Sem incentivo para upgrade

---

## 🔐 Segurança

### 1. Isolamento de Dados

**Implementação:**
```python
def get_queryset(self):
    if self.request.user.organization:
        return Model.objects.filter(
            organization=self.request.user.organization
        )
```

**Proteções:**
- ✅ Filtro automático por org
- ✅ Admin não vê dados de outras orgs
- ✅ User não vê dados de outras orgs

---

### 2. Validação de Limites

**Implementação:**
```python
class CanManageUsers(BasePermission):
    def has_permission(self, request, view):
        if request.method == 'POST':
            current = org.users.count()
            max_users = org.subscription.max_users
            return current < max_users
```

**Proteções:**
- ✅ Valida antes de criar
- ✅ Retorna 403 se exceder
- ✅ Mensagem clara ao usuário

---

## 📊 Trade-offs

### Escolha: Row-Level Security

**Ganhamos:**
- Simplicidade
- Custo baixo
- Rápido de implementar

**Perdemos:**
- Isolamento total
- Backup por org
- Customização por org

**Quando migrar para Schemas:**
- \> 500 organizações
- Clientes enterprise
- Requisitos de compliance

---

## 🎯 Metodologia

### 1. Análise de Requisitos
- Isolamento de dados
- Monetização
- Escalabilidade

### 2. Pesquisa de Alternativas
- Single-tenant
- Schema separation
- Row-level security

### 3. Prototipagem
- Implementação básica
- Testes de carga
- Validação de custos

### 4. Decisão
- Row-level security escolhida
- Documentação de trade-offs
- Plano de migração futura

---

## 🔮 Evolução Futura

### Fase 1 (Atual): Row-Level Security
- 1 banco compartilhado
- Filtro por `organization_id`
- Até 1000 orgs

### Fase 2 (Futuro): Schema Separation
- 1 schema por org
- Migrations automáticas
- Até 5000 orgs

### Fase 3 (Futuro): Database Separation
- 1 banco por org (ou grupo de orgs)
- Roteamento dinâmico
- Ilimitado

**Trigger para migração:**
- Performance degrada
- Requisitos de compliance
- Clientes enterprise
