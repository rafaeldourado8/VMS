# 🚀 Sprint 5: FastAPI Endpoints + Middleware (7 dias)

## 📋 Objetivo

Criar API REST com FastAPI para autenticação e implementar middleware JWT para proteger todas as rotas.

---

## 🎯 Entregáveis

### Dia 1-2: FastAPI Auth Endpoints

#### Estrutura
```
admin/
└── presentation/
    └── fastapi/
        ├── __init__.py
        ├── router.py          # Auth routes
        ├── schemas.py         # Pydantic models
        ├── dependencies.py    # JWT dependency
        └── middleware.py      # JWT middleware
```

#### Endpoints
```python
POST   /api/auth/register      # Criar usuário
POST   /api/auth/login         # Autenticar
GET    /api/auth/me            # Dados do usuário logado
PUT    /api/auth/permissions   # Atualizar permissões (admin only)
POST   /api/auth/refresh       # Refresh token (futuro)
```

---

### Dia 3-4: Middleware JWT

#### JWT Middleware
```python
# admin/presentation/fastapi/middleware.py
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

class JWTMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Rotas públicas
        if request.url.path in ["/api/auth/login", "/api/auth/register"]:
            return await call_next(request)
        
        # Verifica token
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if not token:
            raise HTTPException(401, "Token não fornecido")
        
        try:
            payload = jwt_service.verify_token(token)
            request.state.user_id = payload["user_id"]
            request.state.is_admin = payload["is_admin"]
        except ValueError as e:
            raise HTTPException(401, str(e))
        
        return await call_next(request)
```

#### Dependency Injection
```python
# admin/presentation/fastapi/dependencies.py
from fastapi import Depends, HTTPException, Request

def get_current_user(request: Request) -> str:
    """Retorna user_id do token JWT."""
    if not hasattr(request.state, "user_id"):
        raise HTTPException(401, "Não autenticado")
    return request.state.user_id

def require_admin(request: Request):
    """Valida se usuário é admin."""
    if not hasattr(request.state, "is_admin") or not request.state.is_admin:
        raise HTTPException(403, "Acesso negado")
```

---

### Dia 5-6: Integração com Outros Módulos

#### Container de Dependências
```python
# src/shared/infrastructure/container.py
class Container:
    def __init__(self):
        self._instances = {}
    
    def get_user_repository(self):
        if "user_repo" not in self._instances:
            self._instances["user_repo"] = DjangoUserRepository()
        return self._instances["user_repo"]
    
    def get_jwt_service(self):
        if "jwt_service" not in self._instances:
            self._instances["jwt_service"] = JWTService(
                secret_key=settings.JWT_SECRET,
                expires_in=3600
            )
        return self._instances["jwt_service"]
    
    def get_create_user_use_case(self):
        return CreateUserUseCase(self.get_user_repository())
    
    def get_authenticate_user_use_case(self):
        return AuthenticateUserUseCase(
            self.get_user_repository(),
            self.get_jwt_service()
        )
```

#### Aplicar Middleware em Outros Módulos
```python
# cameras/presentation/fastapi/router.py
from admin.presentation.fastapi.dependencies import get_current_user

@router.post("/cameras")
async def create_camera(
    data: CreateCameraSchema,
    user_id: str = Depends(get_current_user)
):
    # Valida acesso do usuário à cidade
    user = user_repo.find_by_id(user_id)
    if not user.can_access_city(data.city_id):
        raise HTTPException(403, "Sem acesso a esta cidade")
    
    use_case = CreateCameraUseCase(camera_repo)
    camera_id = use_case.execute(CreateCameraRequest(**data.dict()))
    return {"id": camera_id}
```

---

### Dia 7: Testes de Integração

#### Testes de API
```python
# admin/tests/integration/test_auth_api.py
import pytest
from fastapi.testclient import TestClient

def test_register_user(client: TestClient):
    response = client.post("/api/auth/register", json={
        "email": "test@example.com",
        "name": "Test User",
        "password": "senha123",
        "city_ids": ["sao-paulo"]
    })
    assert response.status_code == 201
    assert "id" in response.json()

def test_login(client: TestClient):
    # Cria usuário
    client.post("/api/auth/register", json={...})
    
    # Login
    response = client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "senha123"
    })
    assert response.status_code == 200
    assert "token" in response.json()
    assert "user" in response.json()

def test_get_me(client: TestClient, auth_token: str):
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"

def test_unauthorized_access(client: TestClient):
    response = client.get("/api/auth/me")
    assert response.status_code == 401
```

---

## 📦 Implementação Detalhada

### 1. Pydantic Schemas
```python
# admin/presentation/fastapi/schemas.py
from pydantic import BaseModel, EmailStr

class RegisterSchema(BaseModel):
    email: EmailStr
    name: str
    password: str
    city_ids: list[str] = []
    is_admin: bool = False

class LoginSchema(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    city_ids: list[str]
    is_admin: bool
    is_active: bool

class LoginResponse(BaseModel):
    token: str
    user: UserResponse
```

### 2. Router
```python
# admin/presentation/fastapi/router.py
from fastapi import APIRouter, Depends, HTTPException
from .schemas import RegisterSchema, LoginSchema, LoginResponse, UserResponse
from .dependencies import get_current_user, require_admin

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/register", response_model=UserResponse, status_code=201)
async def register(data: RegisterSchema):
    use_case = container.get_create_user_use_case()
    try:
        user = use_case.execute(CreateUserDTO(**data.dict()))
        return UserResponse(**user.__dict__)
    except ValueError as e:
        raise HTTPException(400, str(e))

@router.post("/login", response_model=LoginResponse)
async def login(data: LoginSchema):
    use_case = container.get_authenticate_user_use_case()
    try:
        result = use_case.execute(AuthenticateDTO(**data.dict()))
        return LoginResponse(
            token=result["token"],
            user=UserResponse(**result["user"].__dict__)
        )
    except ValueError as e:
        raise HTTPException(401, str(e))

@router.get("/me", response_model=UserResponse)
async def get_me(user_id: str = Depends(get_current_user)):
    user = container.get_user_repository().find_by_id(user_id)
    if not user:
        raise HTTPException(404, "Usuário não encontrado")
    return UserResponse(**user.__dict__)

@router.put("/permissions/{user_id}", dependencies=[Depends(require_admin)])
async def update_permissions(user_id: str, city_ids: list[str]):
    use_case = container.get_update_user_permissions_use_case()
    user = use_case.execute(user_id, city_ids)
    return UserResponse(**user.__dict__)
```

### 3. Main App
```python
# src/main.py
from fastapi import FastAPI
from admin.presentation.fastapi.router import router as auth_router
from admin.presentation.fastapi.middleware import JWTMiddleware

app = FastAPI(title="VMS API", version="1.0.0")

# Middleware
app.add_middleware(JWTMiddleware)

# Routers
app.include_router(auth_router)

@app.get("/health")
async def health():
    return {"status": "ok"}
```

---

## ✅ Checklist

### FastAPI Endpoints
- [ ] POST /api/auth/register
- [ ] POST /api/auth/login
- [ ] GET /api/auth/me
- [ ] PUT /api/auth/permissions
- [ ] Pydantic schemas
- [ ] Error handling

### Middleware
- [ ] JWTMiddleware
- [ ] get_current_user dependency
- [ ] require_admin dependency
- [ ] Rotas públicas (whitelist)

### Integração
- [ ] Container de dependências
- [ ] Aplicar em cameras
- [ ] Aplicar em streaming
- [ ] Aplicar em lpr

### Testes
- [ ] test_register_user
- [ ] test_login
- [ ] test_get_me
- [ ] test_unauthorized_access
- [ ] test_admin_only_routes
- [ ] 15+ testes de integração

---

## 🎯 Critérios de Sucesso

1. ✅ 5 endpoints funcionando
2. ✅ Middleware JWT protegendo rotas
3. ✅ Integração com outros módulos
4. ✅ 15+ testes de integração
5. ✅ Documentação OpenAPI automática

---

## 📊 Métricas Esperadas

```
Endpoints: 5
Testes: 15+
Coverage: >90%
Latência: <50ms
```

---

## 🚀 Próximo: Sprint 6

**YOLO Real + Recording Service**

---

**Status:** 📋 PLANEJADO  
**Início:** Após Sprint 4  
**Duração:** 7 dias
