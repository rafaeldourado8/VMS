# Sprint 2: Cidades (Multi-tenant)

## 🎯 Objetivo
Implementar sistema multi-tenant com 1 banco de dados por cidade e gestão de planos.

## 📋 Responsabilidade
Gestão de cidades (tenants) e planos de assinatura.

## 🏗️ Arquitetura DDD

### Domain Layer
```python
# entities.py
class City:
    id: UUID
    name: str
    slug: str
    plan: PlanType
    max_cameras: int
    max_lpr_cameras: int
    retention_days: int
    created_at: datetime
    is_active: bool

# value_objects.py
class PlanType(Enum):
    BASIC = "basic"      # 7 dias, 3 usuários
    PRO = "pro"          # 15 dias, 5 usuários
    PREMIUM = "premium"  # 30 dias, 10 usuários, relatórios

# interfaces.py
class ICityRepository(ABC):
    @abstractmethod
    def create(self, city: City) -> City:
        pass
    
    @abstractmethod
    def get_by_slug(self, slug: str) -> Optional[City]:
        pass
```

### Infrastructure Layer
```python
# models.py (Django)
class CityModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    plan = models.CharField(max_length=20, choices=PlanType.choices)
    max_cameras = models.IntegerField(default=1000)
    max_lpr_cameras = models.IntegerField(default=20)
    retention_days = models.IntegerField(default=7)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'cities'
        # Armazenado no DB default (metadados)
```

### Application Layer
```python
# use_cases.py
class CreateCityUseCase:
    def __init__(self, repository: ICityRepository):
        self.repository = repository
    
    def execute(self, name: str, plan: PlanType) -> City:
        slug = slugify(name)
        
        # Criar cidade
        city = City(
            name=name,
            slug=slug,
            plan=plan,
            max_cameras=self._get_max_cameras(plan),
            max_lpr_cameras=20,
            retention_days=self._get_retention_days(plan)
        )
        
        # Criar banco de dados tenant
        self._create_tenant_database(slug)
        
        return self.repository.create(city)
    
    def _create_tenant_database(self, slug: str):
        db_name = f"cidade_{slug}"
        # Criar DB e rodar migrations
```

## 🗄️ Estrutura de Bancos

### DB Default (Metadados)
```
vms_default/
├── cities
├── users
├── api_keys
└── sessions
```

### DB por Cidade (Tenant)
```
cidade_{slug}/
├── cameras
├── detections
├── recordings
├── clips
└── events
```

## 📊 Planos

| Plano | Retenção | Usuários | Câmeras | LPR | Diferencial |
|-------|----------|----------|---------|-----|-------------|
| Basic | 7 dias | 3 | 1000 | 20 | - |
| Pro | 15 dias | 5 | 1000 | 20 | - |
| Premium | 30 dias | 10 | 1000 | 20 | Relatórios |

## 🔧 Multi-tenant Router

```python
# routers.py
class TenantRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'core':
            return 'default'
        
        # Pegar cidade do contexto da request
        city_slug = get_current_city_slug()
        return f'cidade_{city_slug}'
    
    def db_for_write(self, model, **hints):
        return self.db_for_read(model, **hints)
```

## ✅ Regras de Negócio

1. **1 DB por cidade**: Isolamento total de dados
2. **Max 1000 câmeras**: Limite por cidade
3. **Max 20 LPR**: Câmeras RTSP com IA ativa
4. **Retenção**: 7/15/30 dias conforme plano
5. **Slug único**: Identificador da cidade na URL

## 🚀 Endpoints

```
POST   /api/cities/              # Criar cidade
GET    /api/cities/              # Listar cidades
GET    /api/cities/{slug}/       # Detalhes cidade
PATCH  /api/cities/{slug}/       # Atualizar cidade
DELETE /api/cities/{slug}/       # Deletar cidade (soft delete)
```

## 📝 Exemplo de Uso

```python
# Criar cidade
POST /api/cities/
{
    "name": "São Paulo",
    "plan": "premium"
}

# Response
{
    "id": "uuid",
    "name": "São Paulo",
    "slug": "sao-paulo",
    "plan": "premium",
    "max_cameras": 1000,
    "max_lpr_cameras": 20,
    "retention_days": 30,
    "database": "cidade_sao_paulo"
}
```

## 🔗 Integração

- **Frontend**: Seletor de cidade no header
- **Backend**: Middleware para injetar tenant no contexto
- **LPR**: Busca câmeras do tenant correto
- **Streaming**: Grava no DB do tenant
