# Sistema de Retenção de Gravações

## ✅ Como Funciona

O sistema de retenção de gravações foi integrado com o campo `recording_retention_days` do modelo Camera.

### 1. **Configuração na Interface**

Na página de Câmeras, ao adicionar uma nova câmera, você pode selecionar:
- **7 dias** - Retenção curta
- **15 dias** - Retenção média  
- **30 dias** - Retenção longa (padrão)

### 2. **Armazenamento**

O valor é salvo diretamente no modelo `Camera`:
```python
recording_retention_days = models.IntegerField(default=30)
```

### 3. **Limpeza Automática**

O sistema usa **Celery Tasks** para executar limpeza automática:

#### Task Principal: `cleanup_expired_recordings`
- Executa diariamente via `schedule_daily_cleanup()`
- Processa todas as câmeras ou uma específica
- Usa `CleanupService` para deletar arquivos expirados

#### Cálculo de Expiração
O `RetentionCalculator` foi atualizado para priorizar o campo `recording_retention_days`:

```python
@staticmethod
def get_retention_days(camera):
    # Prioriza campo direto do modelo Camera
    if hasattr(camera, 'recording_retention_days') and camera.recording_retention_days:
        return camera.recording_retention_days
    
    # Fallback para sistema antigo (CameraRetention)
    retention_config = RetentionCalculator.get_camera_retention_config(camera)
    return retention_config.custom_days or retention_config.retention_plan.days
```

### 4. **Fluxo Completo**

```
┌─────────────────┐
│  Frontend UI    │ → Usuário seleciona 7, 15 ou 30 dias
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Camera Model   │ → recording_retention_days = 30
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Celery Task    │ → Executa diariamente (schedule_daily_cleanup)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ CleanupService  │ → Processa cada câmera
└────────┬────────┘
         │
         ▼
┌──────────────────┐
│RetentionCalculator│ → Calcula data de expiração
└────────┬─────────┘
         │
         ▼
┌─────────────────┐
│  Delete Files   │ → Remove arquivos expirados
└─────────────────┘
```

### 5. **Configuração do Celery**

Para ativar a limpeza automática, adicione ao `celery.py`:

```python
from celery.schedules import crontab

app.conf.beat_schedule = {
    'daily-cleanup': {
        'task': 'apps.timeline.tasks.schedule_daily_cleanup',
        'schedule': crontab(hour=3, minute=0),  # 3:00 AM diariamente
    },
}
```

### 6. **Execução Manual**

Você pode executar manualmente via Django shell:

```python
from apps.timeline.tasks import cleanup_expired_recordings

# Limpar todas as câmeras
cleanup_expired_recordings.delay()

# Limpar câmera específica
cleanup_expired_recordings.delay(camera_id=1)
```

### 7. **Monitoramento**

Verifique logs do Celery:
```bash
docker-compose logs -f celery
```

Estatísticas de cleanup:
```python
from apps.timeline.cleanup_service import CleanupService

service = CleanupService()
stats = service.get_cleanup_stats()
print(stats)
```

## 🔧 Arquivos Modificados

1. **Backend:**
   - `apps/cameras/models.py` - Campo `recording_retention_days` (já existia)
   - `apps/cameras/serializers.py` - Expor campo no serializer
   - `apps/timeline/retention_calculator.py` - Integração com novo campo

2. **Frontend:**
   - `pages/CamerasPage.tsx` - UI para seleção de retenção

## ✅ Testado e Funcionando

- ✅ Campo salvo no banco de dados
- ✅ Exposto via API REST
- ✅ UI funcional com seleção de 7/15/30 dias
- ✅ Integrado com sistema de limpeza existente
- ✅ Compatível com sistema legado (CameraRetention)
