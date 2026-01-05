# ✅ Tarefas DDD Refactoring - VMS Backend

## 📅 Fase 1: Preparação (1-2 dias)

### Análise e Planejamento
- [x] Analisar código atual (models, services)
- [x] Identificar bounded contexts
- [x] Criar plano de refatoração
- [ ] Revisar plano com equipe
- [ ] Configurar ferramentas de análise (radon, pytest-cov)

### Setup Inicial
- [ ] Criar estrutura de diretórios domain/
- [ ] Criar estrutura de diretórios application/
- [ ] Criar estrutura de diretórios infrastructure/
- [ ] Configurar pytest com fixtures
- [ ] Configurar coverage report

---

## 📅 Fase 2: Monitoring Context - Domain (3-4 dias)

### Entidades
- [ ] `domain/monitoring/entities/camera.py`
  - [ ] Classe Camera com lógica de negócio
  - [ ] Métodos: activate(), deactivate(), update_location()
  - [ ] Validações de domínio
  - [ ] Testes unitários (CC < 10)

### Value Objects
- [ ] `domain/monitoring/value_objects/stream_url.py`
  - [ ] Validação de URL RTSP
  - [ ] Imutabilidade
  - [ ] Testes unitários
  
- [ ] `domain/monitoring/value_objects/location.py`
  - [ ] Nome e descrição da localização
  - [ ] Testes unitários
  
- [ ] `domain/monitoring/value_objects/geo_coordinates.py`
  - [ ] Validação de latitude/longitude
  - [ ] Testes unitários

### Repositórios (Interface)
- [ ] `domain/monitoring/repositories/camera_repository.py`
  - [ ] Interface abstrata
  - [ ] Métodos: save(), find_by_id(), find_by_owner(), delete()

### Serviços de Domínio
- [ ] `domain/monitoring/services/camera_provisioning_service.py`
  - [ ] Lógica de provisionamento
  - [ ] Validações de negócio
  - [ ] Testes unitários (CC < 10)

### Exceções
- [ ] `domain/monitoring/exceptions.py`
  - [ ] CameraNotFoundException
  - [ ] InvalidStreamUrlException
  - [ ] ProvisioningFailedException

---

## 📅 Fase 3: Detection Context - Domain (3-4 dias)

### Entidades
- [ ] `domain/detection/entities/detection.py`
  - [ ] Classe Detection
  - [ ] Métodos: validate(), is_high_confidence()
  - [ ] Testes unitários (CC < 10)

- [ ] `domain/detection/entities/vehicle.py`
  - [ ] Classe Vehicle
  - [ ] Métodos: classify_type()
  - [ ] Testes unitários

### Value Objects
- [ ] `domain/detection/value_objects/license_plate.py`
  - [ ] Validação de formato
  - [ ] Normalização
  - [ ] Testes unitários

- [ ] `domain/detection/value_objects/confidence.py`
  - [ ] Validação 0.0-1.0
  - [ ] Métodos: is_high(), is_low()
  - [ ] Testes unitários

- [ ] `domain/detection/value_objects/vehicle_type.py`
  - [ ] Enum de tipos
  - [ ] Validação
  - [ ] Testes unitários

### Repositórios (Interface)
- [ ] `domain/detection/repositories/detection_repository.py`
  - [ ] Interface abstrata
  - [ ] Métodos: save(), find_by_camera(), find_by_plate()

### Serviços de Domínio
- [ ] `domain/detection/services/detection_processing_service.py`
  - [ ] Lógica de processamento
  - [ ] Validações
  - [ ] Testes unitários (CC < 10)

### Exceções
- [ ] `domain/detection/exceptions.py`
  - [ ] InvalidPlateFormatException
  - [ ] LowConfidenceException

---

## 📅 Fase 4: Application Layer (2-3 dias)

### Monitoring - Commands
- [ ] `application/monitoring/commands/create_camera_command.py`
  - [ ] DTO de entrada
  - [ ] Validações básicas

- [ ] `application/monitoring/commands/delete_camera_command.py`

### Monitoring - Handlers
- [ ] `application/monitoring/handlers/create_camera_handler.py`
  - [ ] Orquestração do use case
  - [ ] Injeção de dependências
  - [ ] Testes unitários (mock repositories)

- [ ] `application/monitoring/handlers/delete_camera_handler.py`

### Monitoring - Queries
- [ ] `application/monitoring/queries/list_cameras_query.py`
  - [ ] Filtros e paginação
  - [ ] Handler
  - [ ] Testes unitários

### Detection - Commands
- [ ] `application/detection/commands/process_detection_command.py`

### Detection - Handlers
- [ ] `application/detection/handlers/process_detection_handler.py`
  - [ ] Orquestração
  - [ ] Testes unitários

### Detection - Queries
- [ ] `application/detection/queries/list_detections_query.py`

---

## 📅 Fase 5: Infrastructure Layer (3-4 dias)

### Persistence - Django
- [ ] `infrastructure/persistence/django/models/camera_model.py`
  - [ ] Mover de apps/cameras/models.py
  - [ ] Manter compatibilidade

- [ ] `infrastructure/persistence/django/models/detection_model.py`
  - [ ] Mover de apps/deteccoes/models.py

### Repositories - Implementação
- [ ] `infrastructure/persistence/django/repositories/django_camera_repository.py`
  - [ ] Implementar interface do domínio
  - [ ] Mapeamento entidade <-> model
  - [ ] Testes de integração

- [ ] `infrastructure/persistence/django/repositories/django_detection_repository.py`
  - [ ] Implementar interface
  - [ ] Testes de integração

### External Services
- [ ] `infrastructure/external_services/streaming_service_client.py`
  - [ ] Extrair lógica HTTP de CameraService
  - [ ] Retry logic
  - [ ] Testes com mocks

### Messaging
- [ ] `infrastructure/messaging/celery/tasks.py`
  - [ ] Refatorar tasks para usar handlers
  - [ ] Testes

---

## 📅 Fase 6: Interface Layer (2 dias)

### API Views
- [ ] `interfaces/api/v1/cameras/views.py`
  - [ ] Refatorar para usar handlers
  - [ ] Manter compatibilidade
  - [ ] Testes de API

- [ ] `interfaces/api/v1/detections/views.py`
  - [ ] Refatorar para usar handlers
  - [ ] Testes de API

### Dependency Injection
- [ ] Configurar container DI (django-injector ou manual)
- [ ] Registrar repositórios
- [ ] Registrar handlers

---

## 📅 Fase 7: Qualidade e Testes (2-3 dias)

### Análise de Complexidade
- [ ] Executar radon em todo código
- [ ] Identificar métodos com CC > 10
- [ ] Refatorar métodos complexos
- [ ] Re-executar análise

### Cobertura de Testes
- [ ] Executar pytest-cov
- [ ] Identificar gaps de cobertura
- [ ] Adicionar testes faltantes
- [ ] Atingir > 80% cobertura

### Documentação
- [ ] Atualizar CONTEXT.md
- [ ] Documentar bounded contexts
- [ ] Criar diagramas (opcional)
- [ ] README de cada camada

---

## 📊 Métricas de Sucesso

### Cobertura de Testes
- [ ] Domain layer: > 90%
- [ ] Application layer: > 85%
- [ ] Infrastructure layer: > 70%
- [ ] Total: > 80%

### Complexidade Ciclomática
- [ ] Todos os métodos: CC < 10
- [ ] Média do projeto: CC < 5

### Qualidade de Código
- [ ] Zero erros de lint (flake8/ruff)
- [ ] Type hints em 100% do código
- [ ] Docstrings em classes públicas

---

## 🎯 Entregáveis Finais

- [ ] Código refatorado com DDD
- [ ] Suite de testes completa
- [ ] Relatório de cobertura
- [ ] Relatório de CC
- [ ] Documentação atualizada
- [ ] API funcionando sem breaking changes

---

## 📝 Notas

**Tempo estimado total**: 16-22 dias úteis

**Prioridade**: Manter sistema funcionando durante refatoração

**Estratégia**: Implementar novo código ao lado do antigo, migrar gradualmente
