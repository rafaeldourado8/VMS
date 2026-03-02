# Problemas de Performance

## 🔴 Crítico

### 1. Queries N+1 no Django ORM
**Impacto:** Lentidão em listagens, alto uso de CPU/DB

**Exemplo:**
```python
# ❌ N+1 Query
cameras = Camera.objects.all()
for camera in cameras:
    print(camera.location.name)  # Query adicional por câmera

# ✅ Otimizado
cameras = Camera.objects.select_related('location').all()
for camera in cameras:
    print(camera.location.name)  # Sem queries adicionais
```

### 2. Falta de Índices em Tabelas Críticas
**Ação Requerida:**
```python
class Camera(models.Model):
    name = models.CharField(max_length=100, db_index=True)
    rtsp_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['name', 'created_at']),
        ]
```

### 3. Cache Mal Configurado
**Ação Requerida:**
```python
from django.core.cache import cache

@cache_memoize(timeout=300)
def get_active_cameras():
    return Camera.objects.filter(is_active=True)
```

## 🟠 Alto

### 4. Memory Leaks em Serviços de Streaming
**Ação Requerida:**
- Implementar garbage collection adequado
- Fechar conexões RTSP corretamente
- Limitar buffer sizes

### 5. Conexões de Banco Não Pooled
**Ação Requerida:**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'CONN_MAX_AGE': 600,
        'OPTIONS': {
            'connect_timeout': 10,
        }
    }
}
```

## 📋 Checklist

- [ ] Queries otimizadas (select_related/prefetch_related)
- [ ] Índices em campos frequentemente consultados
- [ ] Cache implementado
- [ ] Connection pooling configurado
- [ ] Memory leaks corrigidos
- [ ] Timeouts adequados
- [ ] Resource limits configurados
