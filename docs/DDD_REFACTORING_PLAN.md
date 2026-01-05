# 🏗️ Plano de Refatoração DDD - Backend VMS

## 📋 Objetivo
Aplicar Domain-Driven Design (DDD) no backend Django, isolando o domínio, aplicando SOLID e criando testes unitários com análise de Complexidade Ciclomática (CC).

## 🎯 Bounded Contexts Identificados

### 1. **Monitoring Context** (Monitoramento)
- **Entidades**: Camera, StreamSession
- **Value Objects**: StreamUrl, Location, GeoCoordinates
- **Agregados**: Camera (raiz)
- **Serviços de Domínio**: CameraProvisioningService
- **Repositórios**: CameraRepository

### 2. **Detection Context** (Detecção)
- **Entidades**: Detection, Vehicle
- **Value Objects**: LicensePlate, Confidence, VehicleType
- **Agregados**: Detection (raiz)
- **Serviços de Domínio**: DetectionProcessingService
- **Repositórios**: DetectionRepository

### 3. **Configuration Context** (Configuração)
- **Entidades**: ROI, VirtualLine, TripWire
- **Value Objects**: Polygon, Line, Point
- **Agregados**: CameraConfiguration (raiz)
- **Serviços de Domínio**: ROIConfigurationService

### 4. **Identity Context** (Identidade)
- **Entidades**: User, Permission
- **Value Objects**: Email, Role
- **Agregados**: User (raiz)

## 📁 Nova Estrutura de Diretórios

```
backend/
├── domain/                          # Camada de Domínio (puro Python)
│   ├── monitoring/
│   │   ├── entities/
│   │   │   ├── camera.py
│   │   │   └── stream_session.py
│   │   ├── value_objects/
│   │   │   ├── stream_url.py
│   │   │   ├── location.py
│   │   │   └── geo_coordinates.py
│   │   ├── repositories/
│   │   │   └── camera_repository.py  # Interface
│   │   ├── services/
│   │   │   └── camera_provisioning_service.py
│   │   └── exceptions.py
│   │
│   ├── detection/
│   │   ├── entities/
│   │   │   ├── detection.py
│   │   │   └── vehicle.py
│   │   ├── value_objects/
│   │   │   ├── license_plate.py
│   │   │   ├── confidence.py
│   │   │   └── vehicle_type.py
│   │   ├── repositories/
│   │   │   └── detection_repository.py  # Interface
│   │   ├── services/
│   │   │   └── detection_processing_service.py
│   │   └── exceptions.py
│   │
│   └── shared/                      # Shared Kernel
│       ├── value_objects/
│       │   └── timestamp.py
│       └── exceptions.py
│
├── application/                     # Camada de Aplicação (Use Cases)
│   ├── monitoring/
│   │   ├── commands/
│   │   │   ├── create_camera_command.py
│   │   │   └── delete_camera_command.py
│   │   ├── queries/
│   │   │   └── list_cameras_query.py
│   │   └── handlers/
│   │       ├── create_camera_handler.py
│   │       └── list_cameras_handler.py
│   │
│   └── detection/
│       ├── commands/
│       │   └── process_detection_command.py
│       ├── queries/
│       │   └── list_detections_query.py
│       └── handlers/
│           └── process_detection_handler.py
│
├── infrastructure/                  # Camada de Infraestrutura
│   ├── persistence/
│   │   ├── django/
│   │   │   ├── models/
│   │   │   │   ├── camera_model.py
│   │   │   │   └── detection_model.py
│   │   │   └── repositories/
│   │   │       ├── django_camera_repository.py
│   │   │       └── django_detection_repository.py
│   │   └── migrations/
│   │
│   ├── messaging/
│   │   ├── rabbitmq/
│   │   │   └── detection_publisher.py
│   │   └── celery/
│   │       └── tasks.py
│   │
│   └── external_services/
│       └── streaming_service_client.py
│
├── interfaces/                      # Camada de Interface (API)
│   ├── api/
│   │   ├── v1/
│   │   │   ├── cameras/
│   │   │   │   ├── views.py
│   │   │   │   ├── serializers.py
│   │   │   │   └── urls.py
│   │   │   └── detections/
│   │   │       ├── views.py
│   │   │       ├── serializers.py
│   │   │       └── urls.py
│   │   └── schemas/
│   │       └── api_schemas.py
│   │
│   └── admin/
│       └── camera_admin.py
│
└── tests/
    ├── unit/
    │   ├── domain/
    │   │   ├── monitoring/
    │   │   │   ├── test_camera_entity.py
    │   │   │   └── test_stream_url_vo.py
    │   │   └── detection/
    │   │       └── test_detection_entity.py
    │   └── application/
    │       └── test_create_camera_handler.py
    │
    ├── integration/
    │   └── test_camera_repository.py
    │
    └── conftest.py
```

## 🔄 Etapas de Refatoração

### **Fase 1: Preparação e Análise** ✅
- [x] Analisar código atual
- [ ] Identificar bounded contexts
- [ ] Mapear entidades e value objects
- [ ] Criar estrutura de diretórios

### **Fase 2: Domain Layer - Monitoring Context**
- [ ] Criar entidade Camera (pura)
- [ ] Criar value objects (StreamUrl, Location, GeoCoordinates)
- [ ] Criar interface CameraRepository
- [ ] Criar CameraProvisioningService (domínio)
- [ ] Testes unitários (CC < 10)

### **Fase 3: Domain Layer - Detection Context**
- [ ] Criar entidade Detection
- [ ] Criar value objects (LicensePlate, Confidence, VehicleType)
- [ ] Criar interface DetectionRepository
- [ ] Criar DetectionProcessingService
- [ ] Testes unitários (CC < 10)

### **Fase 4: Application Layer**
- [ ] Implementar Commands (CreateCameraCommand, ProcessDetectionCommand)
- [ ] Implementar Queries (ListCamerasQuery, ListDetectionsQuery)
- [ ] Implementar Handlers (CQRS pattern)
- [ ] Testes unitários

### **Fase 5: Infrastructure Layer**
- [ ] Migrar models Django para infrastructure
- [ ] Implementar DjangoCameraRepository
- [ ] Implementar DjangoDetectionRepository
- [ ] Configurar injeção de dependências
- [ ] Testes de integração

### **Fase 6: Interface Layer**
- [ ] Refatorar views para usar handlers
- [ ] Atualizar serializers
- [ ] Manter compatibilidade com API atual
- [ ] Testes de API

### **Fase 7: Qualidade e Métricas**
- [ ] Análise de CC (radon, mccabe)
- [ ] Cobertura de testes > 80%
- [ ] Refatorar métodos com CC > 10
- [ ] Documentação

## 🎯 Princípios SOLID Aplicados

### **S - Single Responsibility**
- Cada entidade tem uma única responsabilidade
- Services focados em uma operação de domínio

### **O - Open/Closed**
- Interfaces de repositório permitem extensão
- Value objects imutáveis

### **L - Liskov Substitution**
- Implementações de repositório são intercambiáveis
- Polimorfismo em handlers

### **I - Interface Segregation**
- Interfaces específicas por contexto
- Não forçar dependências desnecessárias

### **D - Dependency Inversion**
- Domínio não depende de infraestrutura
- Injeção de dependências via handlers

## 📊 Métricas de Qualidade

### **Complexidade Ciclomática (CC)**
- **Meta**: CC < 10 para todos os métodos
- **Ferramenta**: radon, pytest-cov
- **Ação**: Refatorar métodos com CC > 10

### **Cobertura de Testes**
- **Meta**: > 80% cobertura
- **Foco**: Domain e Application layers
- **Ferramenta**: pytest-cov

### **Tipos de Testes**
- **Unitários**: Domain entities, value objects, services
- **Integração**: Repositories, external services
- **E2E**: API endpoints (mínimo)

## 🚀 Próximos Passos

1. **Aprovação do plano**
2. **Criar estrutura de diretórios**
3. **Iniciar Fase 2: Domain Layer - Monitoring Context**
4. **Implementar testes primeiro (TDD)**
5. **Migração gradual sem quebrar API**

## 📝 Notas Importantes

- **Migração gradual**: Manter código antigo funcionando durante refatoração
- **Backward compatibility**: API externa não muda
- **Feature flags**: Permitir toggle entre implementações
- **Documentação**: Atualizar docs conforme refatoração
