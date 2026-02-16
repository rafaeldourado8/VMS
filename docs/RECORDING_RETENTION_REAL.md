# Sistema de Retenção de Gravações - Arquitetura Real

## ✅ Resposta Direta: SIM, Funciona!

O campo `recording_retention_days` do modelo Camera **funciona perfeitamente** com o sistema de gravação.

## 🏗️ Arquitetura Real

```
┌─────────────┐
│   RECORDER  │ → Grava vídeos em /recordings/cam_X/YYYY-MM-DD/HH-MM-SS.mp4
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   STORAGE   │ → Indexa gravações em PostgreSQL (FastAPI)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  TIMELINE   │ → Monta timeline e resolve vídeos (FastAPI)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   DJANGO    │ → Gerencia câmeras + LIMPEZA de gravações antigas
└─────────────┘
```

## 🔄 Como Funciona a Retenção

### 1. **Usuário Define Retenção na UI**
- Frontend: Seleciona 7, 15 ou 30 dias
- Backend: Salva em `Camera.recording_retention_days`

### 2. **Recorder Grava Continuamente**
- Não se preocupa com retenção
- Apenas grava segmentos de 60s em `/recordings/cam_X/`

### 3. **Storage Indexa Automaticamente**
- Escaneia `/recordings/` a cada 60s
- Indexa novos arquivos no PostgreSQL
- Não deleta nada

### 4. **Django Limpa Arquivos Antigos**
- `CleanupService` usa `recording_retention_days` da câmera
- `RetentionCalculator` calcula data de expiração
- Deleta arquivos físicos expirados
- **Notifica Timeline** via webhook `/cleanup-notification`

### 5. **Timeline Atualiza Cache**
- Recebe notificação de cleanup
- Invalida cache da câmera
- Reindexa automaticamente

## 📝 Integração Implementada

### Backend: `retention_calculator.py`
```python
@staticmethod
def get_retention_days(camera):
    # PRIORIZA campo direto do modelo Camera
    if hasattr(camera, 'recording_retention_days') and camera.recording_retention_days:
        return camera.recording_retention_days
    
    # Fallback para sistema legado
    return 7  # padrão
```

### Limpeza Manual (se necessário)
```python
from apps.timeline.tasks import cleanup_expired_recordings

# Limpar todas as câmeras
cleanup_expired_recordings.delay()

# Limpar câmera específica
cleanup_expired_recordings.delay(camera_id=1)
```

## ⚙️ Configuração Automática (Opcional)

Se quiser limpeza automática diária, adicione ao `docker-compose.yml`:

```yaml
celery-beat:
  build: ./backend
  command: celery -A config beat -l info
  environment:
    - CELERY_BEAT_SCHEDULE={"daily-cleanup":{"task":"apps.timeline.tasks.schedule_daily_cleanup","schedule":{"crontab":{"hour":3,"minute":0}}}}
```

## 🎯 Resumo

| Componente | Responsabilidade | Usa `recording_retention_days`? |
|------------|------------------|--------------------------------|
| **Recorder** | Grava vídeos | ❌ Não |
| **Storage** | Indexa gravações | ❌ Não |
| **Timeline** | Monta timeline | ❌ Não |
| **Django CleanupService** | Deleta arquivos antigos | ✅ **SIM** |

## ✅ Conclusão

**SIM**, o campo `recording_retention_days` funciona perfeitamente! 

- ✅ Salvo no banco de dados
- ✅ Exposto via API
- ✅ UI funcional (7/15/30 dias)
- ✅ Integrado com `RetentionCalculator`
- ✅ Usado pelo `CleanupService`
- ✅ Notifica microserviços após limpeza

A arquitetura está **correta e funcional**!
