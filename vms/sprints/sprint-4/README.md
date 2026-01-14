# 🎯 Sprint 4: Admin + Auth (7 dias)

## 📋 Objetivo

Implementar Django Admin completo e sistema de autenticação JWT.

---

## 🚀 Entregáveis

### Dia 1-2: Admin Module Domain

#### User Entity
```python
# admin/domain/entities/user.py
@dataclass
class User:
    id: str
    email: str
    name: str
    city_ids: list[str]  # Pode acessar múltiplas cidades
    is_admin: bool
    is_active: bool = True
    
    def can_access_city(self, city_id: str) -> bool:
        return self.is_admin or city_id in self.city_ids
```

---

### Dia 3-4: Authentication

#### JWT Authentication
```python
# admin/application/use_cases/authenticate_user.py
class AuthenticateUserUseCase:
    def execute(self, email: str, password: str) -> dict:
        user = self._user_repo.find_by_email(email)
        
        if not user or not self._verify_password(password, user.password_hash):
            raise AuthenticationError()
        
        # Gera JWT token
        token = self._jwt_service.generate_token({
            'user_id': user.id,
            'email': user.email,
            'is_admin': user.is_admin
        })
        
        return {
            'token': token,
            'user': user
        }
```

---

### Dia 5-6: Django Admin Completo

#### Admin para todos os módulos
```python
# Cidades Admin
@admin.register(CityModel)
class CityAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'plan', 'camera_count', 'lpr_count']
    actions = ['export_metrics']

# Cameras Admin
@admin.register(CameraModel)
class CameraAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'lpr_status', 'status', 'city']
    actions = ['activate_cameras', 'deactivate_cameras']

# Detections Admin
@admin.register(DetectionModel)
class DetectionAdmin(admin.ModelAdmin):
    list_display = ['plate', 'confidence', 'camera', 'detected_at']
    list_filter = ['confidence', 'detected_at']

# Streams Admin
@admin.register(StreamModel)
class StreamAdmin(admin.ModelAdmin):
    list_display = ['camera_id', 'status', 'started_at']
    actions = ['stop_streams']
```

---

### Dia 7: Permissions + Tests

#### Permission System
```python
# admin/domain/value_objects/permission.py
class Permission(Enum):
    VIEW_CAMERAS = 'view_cameras'
    MANAGE_CAMERAS = 'manage_cameras'
    VIEW_DETECTIONS = 'view_detections'
    MANAGE_BLACKLIST = 'manage_blacklist'
    VIEW_SEARCHES = 'view_searches'
    ADMIN_ALL = 'admin_all'
```

---

## ✅ Checklist

### Domain
- [x] User entity
- [x] Permission VO
- [x] IUserRepository

### Application
- [x] AuthenticateUserUseCase
- [x] CreateUserUseCase
- [x] UpdateUserPermissionsUseCase

### Infrastructure
- [ ] UserModel (Django) - Sprint 5
- [ ] JWT Service (PyJWT) - Sprint 5
- [ ] Admin completo (todos os módulos) - Sprint 5

### Tests
- [x] Testes de autenticação (4 tests)
- [x] Testes de permissões (3 tests)
- [x] Testes de user entity (10 tests)
- [x] 21 testes, 97% coverage

---

## 🎯 Critérios de Sucesso

1. ✅ Domain Layer completo (User, Permission, IUserRepository)
2. ✅ Application Layer completo (3 use cases)
3. ✅ 21 testes, 97% coverage
4. ✅ Complexidade A (2.05)
5. ⏳ Infrastructure (Django + JWT) - Sprint 5

---

## 📝 Nota sobre Sentinela

⚠️ **Sentinela não faz parte do MVP**

O módulo Sentinela (busca retroativa) será desenvolvido em fase futura:
- Requer modelo YOLO treinado específico
- Requer integração com AWS Rekognition
- Requer processamento pesado de vídeos

**MVP inclui:**
- ✅ Cidades (multi-tenant)
- ✅ Cameras (auto-detecção)
- ✅ Streaming (MediaMTX)
- ✅ LPR (detecção em tempo real)
- ✅ Admin + Auth

**Pós-MVP:**
- ⏳ Sentinela (busca retroativa)
- ⏳ Analytics avançado
- ⏳ Relatórios customizados
