# 🏢 Multi-Tenant + Sistema de Planos

**Prioridade:** P0 - CRÍTICA (Base para Recording)  
**Estimativa:** 3 dias  
**Status:** 🔴 Bloqueante para Sprint 3

---

## 🎯 Objetivo

Implementar sistema multi-tenant com 1 banco por cidade e gerenciamento de planos por usuário, controlando dias de gravação e sobrescrita automática.

---

## 💾 Models Essenciais

### Usuario (ATUALIZAR)
```python
class Usuario(AbstractBaseUser, PermissionsMixin):
    PLAN_CHOICES = (
        ('basic', 'Basic'),      # 7 dias
        ('pro', 'Pro'),          # 15 dias  
        ('premium', 'Premium'),  # 30 dias
    )
    
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='basic')
    
    @property
    def recording_days(self):
        return {'basic': 7, 'pro': 15, 'premium': 30}[self.plan]
```

### Camera (ATUALIZAR)
```python
class Camera(models.Model):
    owner = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    stream_url = models.CharField(max_length=500)
    recording_enabled = models.BooleanField(default=True)
```

---

## 🔄 Recording Service com Planos

```python
class RecordingService:
    def cleanup_old_recordings(self, camera: Camera):
        """Remove gravações antigas baseado no plano"""
        days = camera.owner.recording_days
        cutoff = timezone.now() - timedelta(days=days)
        
        Recording.objects.filter(
            camera=camera,
            created_at__lt=cutoff,
            is_clip=False
        ).delete()
```

---

## ⏰ Cron Job Diário

```python
@celery.task
def cleanup_recordings_daily():
    """Roda às 3h da manhã"""
    for camera in Camera.objects.filter(recording_enabled=True):
        RecordingService().cleanup_old_recordings(camera)
```

---

## ✅ Checklist

```
[ ] Adicionar campo plan em Usuario
[ ] Criar property recording_days
[ ] Implementar cleanup_old_recordings
[ ] Criar cron job diário
[ ] Testar sobrescrita automática
```

---

**IMPLEMENTAR AGORA antes do Recording!** 🔥
