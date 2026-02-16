# Backend IAM - Implementação Completa

## 📦 Estrutura Criada

```
backend/apps/iam/
├── __init__.py
├── apps.py
├── models.py              # IAMPermission, IAMRule, UserPermissions, TenantIsolation
├── serializers.py         # Serializers para API
├── views.py               # ViewSets com isolamento
├── urls.py                # Rotas da API
├── admin.py               # Interface admin
├── middleware.py          # Middleware de isolamento
├── mixins.py              # TenantAwareMixin, TenantAwareManager
└── migrations/
    └── __init__.py
```

## 🗄️ Models

### 1. IAMPermission
Permissões granulares do sistema
```python
- code: str (unique)
- name: str
- description: text
- resource: str
```

### 2. IAMRule
Regras de acesso baseadas em condições
```python
- name: str
- description: text
- conditions: JSONField
- actions: ArrayField
- is_active: bool
```

### 3. UserPermissions
Permissões atribuídas a usuários
```python
- user: FK(Usuario)
- permissions: ArrayField
```

### 4. TenantIsolation ⭐
**Isolamento de dados por usuário**
```python
- user: FK(Usuario)
- resource_type: str (camera, recording, detection, etc)
- resource_id: int
- can_read: bool
- can_write: bool
- can_delete: bool
```

## 🔐 Isolamento de Tenant

### Como Funciona

1. **Cada recurso** (câmera, gravação, detecção) tem entrada em `TenantIsolation`
2. **Usuário só vê** recursos que tem permissão
3. **Admin** tem acesso a tudo automaticamente
4. **Granularidade**: read, write, delete por recurso

### Exemplo de Uso

```python
# Criar câmera e conceder acesso
camera = Camera.objects.create(name="Cam 1", owner=user)
camera.grant_access_to_user(user, read=True, write=True, delete=True)

# Verificar acesso
if camera.user_can_access(user, 'write'):
    camera.name = "Nova Cam"
    camera.save()

# Listar câmeras do usuário
cameras = Camera.objects.for_user(user, 'camera')
```

## 🔌 APIs Criadas

### Usuários
```
GET    /api/iam/users/                    # Lista usuários
POST   /api/iam/users/                    # Criar usuário
PUT    /api/iam/users/{id}/               # Atualizar usuário
DELETE /api/iam/users/{id}/               # Deletar usuário
POST   /api/iam/users/{id}/grant_resource_access/  # Conceder acesso
GET    /api/iam/users/{id}/resources/     # Listar recursos do usuário
```

### Regras
```
GET    /api/iam/rules/                    # Lista regras
POST   /api/iam/rules/                    # Criar regra
PUT    /api/iam/rules/{id}/               # Atualizar regra
DELETE /api/iam/rules/{id}/               # Deletar regra
```

### Permissões
```
GET    /api/iam/permissions/user/{user_id}/        # Permissões do usuário
POST   /api/iam/permissions/user/{user_id}/        # Atualizar permissões
```

## 🎯 Integração com Models Existentes

### Camera Model (Atualizado)
```python
from apps.iam.mixins import TenantAwareMixin, TenantAwareManager

class Camera(TenantAwareMixin, models.Model):
    # ... campos existentes ...
    
    objects = TenantAwareManager()
    
    @classmethod
    def get_resource_type(cls):
        return 'camera'
```

### Camera Views (Atualizado)
```python
def get_queryset(self):
    # Filtra automaticamente por tenant
    return Camera.objects.for_user(self.request.user, 'camera')

def create(self, request):
    camera = self.service.create_camera(camera_dto)
    # Concede acesso automático ao criador
    camera.grant_access_to_user(request.user, read=True, write=True, delete=True)
    return Response(...)
```

## 🔧 Configuração

### 1. Adicionar ao settings.py
```python
INSTALLED_APPS = [
    # ...
    'apps.iam',
]

MIDDLEWARE = [
    # ...
    'apps.iam.middleware.TenantIsolationMiddleware',
]
```

### 2. Adicionar URLs
```python
# backend/urls.py
urlpatterns = [
    # ...
    path('api/iam/', include('apps.iam.urls')),
]
```

### 3. Rodar Migrations
```bash
python manage.py makemigrations iam
python manage.py migrate iam
```

### 4. Criar Permissões Padrão
```python
# Via Django shell ou fixture
from apps.iam.models import IAMPermission

permissions = [
    {'code': 'cameras.view', 'name': 'Visualizar Câmeras', 'resource': 'cameras'},
    {'code': 'cameras.create', 'name': 'Criar Câmeras', 'resource': 'cameras'},
    {'code': 'cameras.edit', 'name': 'Editar Câmeras', 'resource': 'cameras'},
    {'code': 'cameras.delete', 'name': 'Deletar Câmeras', 'resource': 'cameras'},
    # ... mais permissões
]

for perm in permissions:
    IAMPermission.objects.get_or_create(**perm)
```

## 📊 Fluxo Completo

### 1. Admin Cria Usuário
```bash
POST /api/iam/users/
{
  "name": "João Silva",
  "email": "joao@example.com",
  "password": "senha123",
  "role": "operator",
  "permissions": ["cameras.view", "cameras.create"]
}
```

### 2. Usuário Cria Câmera
```bash
POST /api/cameras/
{
  "name": "Câmera Entrada",
  "stream_url": "rtsp://..."
}

# Automaticamente cria entrada em TenantIsolation:
# user=joao, resource_type=camera, resource_id=1, can_read=True, can_write=True, can_delete=True
```

### 3. Admin Compartilha Câmera
```bash
POST /api/iam/users/2/grant_resource_access/
{
  "resource_type": "camera",
  "resource_id": 1,
  "can_read": true,
  "can_write": false,
  "can_delete": false
}
```

### 4. Usuário Lista Câmeras
```bash
GET /api/cameras/

# Retorna apenas câmeras que ele tem acesso
# Admin vê todas, usuário comum vê apenas as suas + compartilhadas
```

## 🎨 Benefícios

✅ **Isolamento Total**: Cada usuário vê apenas seus recursos  
✅ **Granularidade**: Controle read/write/delete por recurso  
✅ **Compartilhamento**: Admin pode compartilhar recursos entre usuários  
✅ **Auditoria**: Todas as permissões registradas  
✅ **Escalável**: Suporta múltiplos tenants  
✅ **Seguro**: Middleware valida automaticamente  

## 🔍 Próximos Passos

1. Aplicar `TenantAwareMixin` em outros models:
   - Recording
   - Detection
   - Clip

2. Implementar auditoria de acessos

3. Criar dashboard de permissões

4. Adicionar notificações de compartilhamento

## 🧪 Testes

```python
# Criar usuário
user1 = Usuario.objects.create_user('user1@test.com', 'User 1', 'pass')
user2 = Usuario.objects.create_user('user2@test.com', 'User 2', 'pass')

# User1 cria câmera
camera = Camera.objects.create(name='Cam 1', owner=user1)
camera.grant_access_to_user(user1, read=True, write=True, delete=True)

# User2 não vê a câmera
assert Camera.objects.for_user(user2, 'camera').count() == 0

# Admin compartilha com User2
camera.grant_access_to_user(user2, read=True, write=False, delete=False)

# User2 agora vê, mas não pode editar
assert Camera.objects.for_user(user2, 'camera').count() == 1
assert not camera.user_can_access(user2, 'write')
```
