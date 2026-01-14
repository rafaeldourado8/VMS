# 🏗️ Admin Module - Architecture Diagram

## System Overview

```mermaid
graph TB
    subgraph "Presentation Layer (Sprint 5)"
        API["FastAPI Endpoints<br/>POST /auth/login<br/>POST /auth/register<br/>GET /auth/me"]
        MW["JWT Middleware<br/>Autenticação<br/>Autorização"]
    end
    
    subgraph "Application Layer ✅"
        UC1["CreateUserUseCase<br/>✅ Implementado"]
        UC2["AuthenticateUserUseCase<br/>✅ Implementado"]
        UC3["UpdateUserPermissionsUseCase<br/>✅ Implementado"]
        DTO1["CreateUserDTO"]
        DTO2["AuthenticateDTO"]
    end
    
    subgraph "Domain Layer ✅"
        USER["User Entity<br/>✅ Validações<br/>✅ Multi-tenant"]
        PERM["Permission VO<br/>✅ Enum"]
        REPO["IUserRepository<br/>✅ Interface"]
    end
    
    subgraph "Infrastructure Layer (Sprint 5)"
        JWT["JWTService<br/>PyJWT<br/>⏳ Pendente"]
        DJANGO["UserModel<br/>PostgreSQL<br/>⏳ Pendente"]
        ADMIN["Django Admin<br/>⏳ Pendente"]
    end
    
    API --> MW
    MW --> UC1
    MW --> UC2
    MW --> UC3
    
    UC1 --> DTO1
    UC2 --> DTO2
    UC3 --> USER
    
    UC1 --> REPO
    UC2 --> REPO
    UC2 --> JWT
    UC3 --> REPO
    
    USER --> PERM
    REPO --> USER
    
    REPO -.->|"Implementa"| DJANGO
    JWT -.->|"Usa"| DJANGO
    ADMIN -.->|"Gerencia"| DJANGO
    
    style USER fill:#d3f9d8
    style PERM fill:#d3f9d8
    style REPO fill:#d3f9d8
    style UC1 fill:#d3f9d8
    style UC2 fill:#d3f9d8
    style UC3 fill:#d3f9d8
    style DTO1 fill:#d3f9d8
    style DTO2 fill:#d3f9d8
    style API fill:#fff3bf
    style MW fill:#fff3bf
    style JWT fill:#ffe3e3
    style DJANGO fill:#ffe3e3
    style ADMIN fill:#ffe3e3
```

## Authentication Flow

```mermaid
sequenceDiagram
    participant C as Client
    participant API as FastAPI
    participant UC as AuthenticateUseCase
    participant REPO as UserRepository
    participant JWT as JWTService
    participant DB as PostgreSQL
    
    C->>API: POST /auth/login<br/>{email, password}
    API->>UC: execute(AuthenticateDTO)
    UC->>REPO: find_by_email(email)
    REPO->>DB: SELECT * FROM users
    DB-->>REPO: User data
    REPO-->>UC: User entity
    
    UC->>UC: verify_password(hash)
    
    alt Password OK
        UC->>JWT: generate_token(payload)
        JWT-->>UC: JWT token
        UC-->>API: {token, user}
        API-->>C: 200 OK + token
    else Password Invalid
        UC-->>API: ValueError
        API-->>C: 401 Unauthorized
    end
```

## User Creation Flow

```mermaid
sequenceDiagram
    participant A as Admin
    participant API as FastAPI
    participant UC as CreateUserUseCase
    participant REPO as UserRepository
    participant DB as PostgreSQL
    
    A->>API: POST /auth/register<br/>{email, name, password, city_ids}
    API->>UC: execute(CreateUserDTO)
    
    UC->>REPO: exists_by_email(email)
    REPO->>DB: SELECT COUNT(*) FROM users
    DB-->>REPO: 0
    REPO-->>UC: False
    
    UC->>UC: hash_password(password)
    UC->>UC: create User entity
    
    UC->>REPO: save(user)
    REPO->>DB: INSERT INTO users
    DB-->>REPO: User saved
    REPO-->>UC: User entity
    
    UC-->>API: User created
    API-->>A: 201 Created
```

## Multi-Tenant Access Control

```mermaid
graph LR
    subgraph "User Types"
        NORMAL["Normal User<br/>city_ids: [sp, rj]"]
        ADMIN["Admin User<br/>is_admin: true"]
    end
    
    subgraph "Cities"
        SP["São Paulo"]
        RJ["Rio de Janeiro"]
        BSB["Brasília"]
    end
    
    NORMAL -->|"✅ can_access"| SP
    NORMAL -->|"✅ can_access"| RJ
    NORMAL -->|"❌ cannot_access"| BSB
    
    ADMIN -->|"✅ can_access"| SP
    ADMIN -->|"✅ can_access"| RJ
    ADMIN -->|"✅ can_access"| BSB
    
    style NORMAL fill:#e7f5ff
    style ADMIN fill:#ffe3e3
    style SP fill:#d3f9d8
    style RJ fill:#d3f9d8
    style BSB fill:#d3f9d8
```

## Permission System

```mermaid
graph TB
    subgraph "Permissions"
        P1["VIEW_CAMERAS"]
        P2["MANAGE_CAMERAS"]
        P3["VIEW_DETECTIONS"]
        P4["MANAGE_BLACKLIST"]
        P5["VIEW_RECORDINGS"]
        P6["CREATE_CLIPS"]
        P7["ADMIN_ALL"]
    end
    
    subgraph "Roles"
        VIEWER["Viewer<br/>Apenas visualização"]
        OPERATOR["Operator<br/>Operação básica"]
        MANAGER["Manager<br/>Gestão completa"]
        ADMIN["Admin<br/>Acesso total"]
    end
    
    VIEWER --> P1
    VIEWER --> P3
    VIEWER --> P5
    
    OPERATOR --> P1
    OPERATOR --> P3
    OPERATOR --> P5
    OPERATOR --> P6
    
    MANAGER --> P1
    MANAGER --> P2
    MANAGER --> P3
    MANAGER --> P4
    MANAGER --> P5
    MANAGER --> P6
    
    ADMIN --> P7
    
    style VIEWER fill:#e7f5ff
    style OPERATOR fill:#d3f9d8
    style MANAGER fill:#fff3bf
    style ADMIN fill:#ffe3e3
```

## Data Model

```mermaid
erDiagram
    USER ||--o{ USER_CITY : "has access to"
    USER {
        uuid id PK
        string email UK
        string name
        string password_hash
        boolean is_admin
        boolean is_active
        timestamp created_at
        timestamp updated_at
    }
    
    USER_CITY {
        uuid user_id FK
        uuid city_id FK
    }
    
    CITY {
        uuid id PK
        string name
        string slug UK
        string plan
    }
    
    USER_CITY }o--|| CITY : "references"
```

## Test Coverage Map

```mermaid
graph TB
    subgraph "Domain Tests ✅"
        T1["test_user_entity.py<br/>10 tests"]
        T2["test_permission.py<br/>2 tests"]
    end
    
    subgraph "Application Tests ✅"
        T3["test_create_user_use_case.py<br/>3 tests"]
        T4["test_authenticate_user_use_case.py<br/>4 tests"]
        T5["test_update_user_permissions_use_case.py<br/>3 tests"]
    end
    
    subgraph "Infrastructure Tests ⏳"
        T6["test_jwt_service.py<br/>Sprint 5"]
        T7["test_user_model.py<br/>Sprint 5"]
        T8["test_auth_endpoints.py<br/>Sprint 5"]
    end
    
    T1 --> USER_ENTITY["User Entity<br/>97% coverage"]
    T2 --> PERMISSION["Permission VO<br/>100% coverage"]
    T3 --> CREATE_UC["CreateUserUseCase<br/>100% coverage"]
    T4 --> AUTH_UC["AuthenticateUserUseCase<br/>100% coverage"]
    T5 --> UPDATE_UC["UpdateUserPermissionsUseCase<br/>100% coverage"]
    
    style T1 fill:#d3f9d8
    style T2 fill:#d3f9d8
    style T3 fill:#d3f9d8
    style T4 fill:#d3f9d8
    style T5 fill:#d3f9d8
    style T6 fill:#ffe3e3
    style T7 fill:#ffe3e3
    style T8 fill:#ffe3e3
```

## Deployment Architecture (Sprint 5)

```mermaid
graph TB
    subgraph "Client"
        WEB["Web Browser"]
        MOBILE["Mobile App"]
    end
    
    subgraph "API Gateway"
        NGINX["Nginx<br/>Reverse Proxy"]
    end
    
    subgraph "Application"
        FASTAPI["FastAPI<br/>Auth Endpoints"]
        DJANGO["Django Admin"]
    end
    
    subgraph "Database"
        PG["PostgreSQL<br/>users table"]
        REDIS["Redis<br/>JWT blacklist"]
    end
    
    WEB --> NGINX
    MOBILE --> NGINX
    
    NGINX --> FASTAPI
    NGINX --> DJANGO
    
    FASTAPI --> PG
    FASTAPI --> REDIS
    DJANGO --> PG
    
    style WEB fill:#e7f5ff
    style MOBILE fill:#e7f5ff
    style NGINX fill:#fff3bf
    style FASTAPI fill:#d3f9d8
    style DJANGO fill:#d3f9d8
    style PG fill:#ffe3e3
    style REDIS fill:#ffe3e3
```

---

## Legend

- 🟢 **Green** - Implementado (Sprint 4)
- 🟡 **Yellow** - Em desenvolvimento
- 🔴 **Red** - Pendente (Sprint 5)
- ✅ **Check** - Completo
- ⏳ **Clock** - Aguardando

---

## Notes

1. **Domain + Application** estão 100% implementados e testados
2. **Infrastructure** será implementado na Sprint 5
3. **JWT** usará PyJWT com RS256
4. **PostgreSQL** armazenará usuários no banco default
5. **Redis** será usado para blacklist de tokens
