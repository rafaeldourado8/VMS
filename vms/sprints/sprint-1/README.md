# 🎯 Sprint 1: Core + Multi-tenant (7 dias)

## 📋 Objetivo

Criar a base do sistema com **Domain-Driven Design**, **multi-tenant** (1 DB por cidade) e **planos de armazenamento**.

---

## 🏗️ Arquitetura Multi-Tenant

### Estratégia: Database per Tenant

```
┌─────────────────────────────────────┐
│   DB Admin (default)                │
│   - Users (centralizados)           │
│   - Cities (tenants)                │
│   - Global configs                  │
└─────────────────────────────────────┘
           │
           ├─────────────────────────┐
           │                         │
┌──────────▼──────────┐   ┌─────────▼──────────┐
│  DB cidade_sp       │   │  DB cidade_rj      │
│  - Cameras          │   │  - Cameras         │
│  - Detections       │   │  - Detections      │
│  - Recordings       │   │  - Recordings      │
│  - Clips            │   │  - Clips           │
└─────────────────────┘   └────────────────────┘
```

### Django Database Router

```python
class MultiTenantRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'admin':
            return 'default'
        
        city = get_current_city()
        return f'cidade_{city.slug}'
```

---

## 📦 Entregáveis

### Dia 1-2: Domain Layer (Python Puro)

#### Entities

```python
# domain/entities/city.py
from dataclasses import dataclass
from domain.value_objects import PlanType

@dataclass
class City:
    id: str
    name: str
    slug: str
    plan: PlanType
    max_cameras: int
    max_lpr_cameras: int
    retention_days: int
    
    def can_add_camera(self, current_count: int) -> bool:
        return current_count < self.max_cameras
    
    def can_add_lpr_camera(self, current_lpr_count: int) -> bool:
        return current_lpr_count < self.max_lpr_cameras
```

```python
# domain/entities/camera.py
from dataclasses import dataclass
from domain.value_objects import CameraType, CameraStatus

@dataclass
class Camera:
    id: str
    name: str
    type: CameraType
    status: CameraStatus
    rtsp_url: str
    city_id: str
    
    def activate(self):
        self.status = CameraStatus.ACTIVE
    
    def is_lpr_enabled(self) -> bool:
        return self.type == CameraType.RTSP
```

#### Value Objects

```python
# domain/value_objects/plan_type.py
from enum import Enum

class PlanType(Enum):
    BASIC = "basic"      # 7 dias, 3 users
    PRO = "pro"          # 15 dias, 5 users
    PREMIUM = "premium"  # 30 dias, 10 users
    
    @property
    def retention_days(self) -> int:
        return {
            PlanType.BASIC: 7,
            PlanType.PRO: 15,
            PlanType.PREMIUM: 30
        }[self]
```

#### Repository Interfaces

```python
# domain/repositories/city_repository.py
from abc import ABC, abstractmethod
from domain.entities import City

class ICityRepository(ABC):
    @abstractmethod
    def save(self, city: City) -> None:
        pass
    
    @abstractmethod
    def find_by_id(self, city_id: str) -> City | None:
        pass
```

---

### Dia 3-4: Application Layer

```python
# application/use_cases/create_city.py
from dataclasses import dataclass
from domain.repositories import ICityRepository

@dataclass
class CreateCityRequest:
    name: str
    slug: str
    plan: str

class CreateCityUseCase:
    def __init__(self, repo: ICityRepository):
        self._repo = repo
    
    def execute(self, request: CreateCityRequest) -> str:
        city = City(...)
        self._repo.save(city)
        return city.id
```

---

### Dia 5-6: Infrastructure (Django)

```python
# infrastructure/django/models/city_model.py
from django.db import models

class CityModel(models.Model):
    id = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    plan = models.CharField(max_length=20)
    
    class Meta:
        db_table = 'cities'
        app_label = 'admin'  # DB default
    
    def to_entity(self) -> City:
        return City(...)
```

```python
# infrastructure/django/repositories/django_city_repository.py
class DjangoCityRepository(ICityRepository):
    def save(self, city: City) -> None:
        model = CityModel.from_entity(city)
        model.save()
```

---

### Dia 7: Django Admin

```python
# infrastructure/django/admin/city_admin.py
@admin.register(CityModel)
class CityAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'plan', 'camera_count']
    list_filter = ['plan']
    
    def camera_count(self, obj):
        return self._camera_repo.count_by_city(obj.id)
```

---

## ✅ Checklist

### Domain
- [ ] City entity
- [ ] Camera entity
- [ ] User entity
- [ ] PlanType VO
- [ ] ICityRepository
- [ ] ICameraRepository

### Application
- [ ] CreateCityUseCase
- [ ] AddCameraUseCase
- [ ] ActivateCameraUseCase

### Infrastructure
- [ ] CityModel
- [ ] CameraModel
- [ ] DjangoCityRepository
- [ ] MultiTenantRouter

### Presentation
- [ ] CityAdmin
- [ ] CameraAdmin
- [ ] Migrations

### Testes
- [ ] Unit tests (domain)
- [ ] Integration tests
- [ ] E2E tests

---

## 🎯 Critérios de Sucesso

1. ✅ 3 cidades cadastradas
2. ✅ 50 câmeras distribuídas
3. ✅ Multi-tenant funcionando
4. ✅ Django Admin operacional
5. ✅ Testes > 80%
