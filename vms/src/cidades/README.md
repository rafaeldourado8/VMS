# 🏙️ Módulo Cidades (Multi-tenant)

## 📋 Responsabilidade

Gerenciar cidades (tenants) com planos de armazenamento e limites de recursos.

---

## 🏗️ Arquitetura

```
Domain (Python puro)
  ↓
Application (Use Cases)
  ↓
Infrastructure (Django)
```

---

## 📦 Estrutura

```
cidades/
├── domain/
│   ├── entities/
│   │   └── city.py              ✅ Entity pura
│   ├── value_objects/
│   │   ├── plan_type.py         ✅ Enum de planos
│   │   └── city_slug.py         ✅ Validação de slug
│   ├── repositories/
│   │   └── city_repository.py   ✅ Interface
│   └── events/
│       ├── city_created.py      ✅ Evento de criação
│       └── city_deleted.py      ✅ Evento de deleção
│
├── application/
│   └── use_cases/
│       ├── create_city.py       ✅ Criar cidade
│       └── list_cities.py       ✅ Listar cidades
│
├── infrastructure/
│   └── django/
│       ├── models.py            ✅ CityModel (adapter)
│       ├── repository.py        ✅ Implementação
│       ├── admin.py             ✅ Django Admin
│       └── router.py            ✅ Multi-tenant router
│
└── tests/
    ├── unit/
    │   ├── test_city_entity.py          ✅
    │   ├── test_plan_type.py            ✅
    │   ├── test_city_slug.py            ✅
    │   ├── test_create_city_use_case.py ✅
    │   └── test_list_cities_use_case.py ✅
    └── conftest.py                      ✅
```

---

## 🎯 Domain

### City Entity

```python
@dataclass
class City:
    id: str
    name: str
    slug: str
    plan: str  # 'basic', 'pro', 'premium'
    max_cameras: int = 1000
    max_lpr_cameras: int = 20
```

### Value Objects

**PlanType**
- BASIC: 7 dias, 3 usuários
- PRO: 15 dias, 5 usuários
- PREMIUM: 30 dias, 10 usuários

**CitySlug**
- Validação: lowercase, números, hífens, underscores
- Max 50 caracteres
- Imutável

### Events

**CityCreatedEvent**
- Disparado ao criar cidade
- Usado para criar DB tenant

**CityDeletedEvent**
- Disparado ao deletar cidade
- Usado para limpar recursos

---

## 🔧 Multi-tenant

### Estratégia: Database per Tenant

- **DB default**: cities, users
- **DB cidade_{slug}**: cameras, detections, recordings

### Router

```python
class MultiTenantRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'cidades':
            return 'default'
        
        city_slug = get_current_city()
        return f'cidade_{city_slug}'
```

---

## ✅ Implementado

### Domain
- [x] City entity
- [x] PlanType VO
- [x] CitySlug VO
- [x] ICityRepository
- [x] CityCreatedEvent
- [x] CityDeletedEvent

### Application
- [x] CreateCityUseCase
- [x] ListCitiesUseCase

### Infrastructure
- [x] CityModel (Django)
- [x] DjangoCityRepository
- [x] CityAdmin
- [x] MultiTenantRouter

### Tests
- [x] test_city_entity (6 tests)
- [x] test_plan_type (4 tests)
- [x] test_city_slug (8 tests)
- [x] test_create_city_use_case (2 tests)
- [x] test_list_cities_use_case (2 tests)
- [x] Total: 22 testes unitários

---

## 🧪 Executar Testes

```bash
cd vms/src/cidades
pytest
```

---

## 🚀 Próximo

- [ ] Migrations
- [ ] Seeds (3 cidades teste)
- [ ] Testes de integração (Django)
