# Sprint 2: Django App Base

## Objetivo
Criar o Django app para configurações de timeline e retenção

## Checklist

### 📁 Estrutura Django App
- [ ] Criar `backend/apps/timeline/`
- [ ] Criar `__init__.py`
- [ ] Criar `apps.py`
- [ ] Criar `models.py`
- [ ] Criar `admin.py`
- [ ] Criar `serializers.py`
- [ ] Criar `views.py`
- [ ] Criar `urls.py`
- [ ] Criar `services.py`

### 🗄 Models Django
- [ ] `RetentionPlan` - Planos de retenção
  - [ ] name (CharField)
  - [ ] days (IntegerField)
  - [ ] description (TextField)
  - [ ] is_active (BooleanField)
  - [ ] created_at, updated_at
- [ ] `CameraRetention` - Configuração por câmera
  - [ ] camera (ForeignKey to Camera)
  - [ ] retention_plan (ForeignKey to RetentionPlan)
  - [ ] custom_days (IntegerField, nullable)
  - [ ] enabled (BooleanField)
  - [ ] created_at, updated_at
- [ ] `StorageAudit` - Log de auditoria
  - [ ] camera (ForeignKey to Camera)
  - [ ] action (CharField: created, deleted, expired)
  - [ ] file_path (CharField)
  - [ ] file_size (BigIntegerField)
  - [ ] timestamp (DateTimeField)

### 🔧 Admin Interface
- [ ] RetentionPlan admin
  - [ ] List display: name, days, is_active
  - [ ] Filters: is_active
  - [ ] Search: name
- [ ] CameraRetention admin
  - [ ] List display: camera, retention_plan, enabled
  - [ ] Filters: retention_plan, enabled
  - [ ] Inline em Camera admin
- [ ] StorageAudit admin (readonly)
  - [ ] List display: camera, action, timestamp, file_size
  - [ ] Filters: action, timestamp
  - [ ] Search: camera__name

### 📡 API Endpoints
- [ ] `GET /api/timeline/retention-plans/` - Lista planos
- [ ] `POST /api/timeline/retention-plans/` - Criar plano
- [ ] `GET /api/timeline/cameras/{id}/retention/` - Config da câmera
- [ ] `PUT /api/timeline/cameras/{id}/retention/` - Atualizar config
- [ ] `GET /api/timeline/storage/stats/` - Estatísticas de storage
- [ ] `GET /api/timeline/audit/` - Log de auditoria

### 🔒 Permissions
- [ ] Apenas admin pode criar/editar planos
- [ ] Usuários podem ver configuração das próprias câmeras
- [ ] Auditoria apenas para admin

### 📊 Serializers
- [ ] RetentionPlanSerializer
- [ ] CameraRetentionSerializer
- [ ] StorageStatsSerializer
- [ ] AuditLogSerializer

### 🛠 Services
- [ ] RetentionService
  - [ ] calculate_expiry_date()
  - [ ] get_camera_retention()
  - [ ] update_camera_retention()
- [ ] StorageService
  - [ ] get_storage_stats()
  - [ ] log_file_action()

### 🗃 Migrations
- [ ] Initial migration criada
- [ ] Dados iniciais (planos padrão)
  - [ ] 7 dias
  - [ ] 15 dias
  - [ ] 30 dias

### ⚙️ Settings
- [ ] Adicionar 'timeline' em INSTALLED_APPS
- [ ] Configurar URLs no projeto

### ✅ Testes
- [x] Models salvam corretamente
- [x] Admin interface funciona
- [x] APIs retornam dados corretos
- [x] Permissions funcionam

## Critérios de Aceite
- [x] Admin pode criar planos de retenção
- [x] Câmeras podem ser associadas a planos
- [x] APIs funcionam corretamente
- [x] Migrations aplicam sem erro

## Estimativa: 6 horas