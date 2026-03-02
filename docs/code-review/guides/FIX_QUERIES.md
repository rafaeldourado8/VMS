# Como Otimizar Queries Django

## Problema N+1

```python
# ❌ N+1 Query Problem
cameras = Camera.objects.all()
for camera in cameras:
    print(camera.location.name)  # Query adicional
    print(camera.recordings.count())  # Mais uma query
```

## Soluções

### 1. select_related (ForeignKey, OneToOne)

```python
# ✅ Otimizado com JOIN
cameras = Camera.objects.select_related('location').all()
for camera in cameras:
    print(camera.location.name)  # Sem query adicional
```

### 2. prefetch_related (ManyToMany, Reverse FK)

```python
# ✅ Otimizado com prefetch
cameras = Camera.objects.prefetch_related('recordings').all()
for camera in cameras:
    print(camera.recordings.count())  # Sem query adicional
```

### 3. Combinar Ambos

```python
cameras = Camera.objects.select_related('location').prefetch_related('recordings').all()
```

### 4. only() e defer()

```python
# Carregar apenas campos necessários
cameras = Camera.objects.only('id', 'name', 'rtsp_url')

# Adiar campos pesados
cameras = Camera.objects.defer('thumbnail', 'config_json')
```

### 5. Agregações

```python
from django.db.models import Count, Avg

# ✅ Agregação no banco
stats = Camera.objects.aggregate(
    total=Count('id'),
    avg_fps=Avg('fps')
)
```

### 6. Bulk Operations

```python
# ✅ Bulk create
Camera.objects.bulk_create([
    Camera(name='Cam1'),
    Camera(name='Cam2'),
])

# ✅ Bulk update
cameras = Camera.objects.all()
for camera in cameras:
    camera.is_active = True
Camera.objects.bulk_update(cameras, ['is_active'])
```

## Debug Queries

```python
from django.db import connection

# Ver queries executadas
print(connection.queries)

# Contar queries
print(len(connection.queries))
```

## Checklist

- [ ] Usar select_related para ForeignKey
- [ ] Usar prefetch_related para ManyToMany
- [ ] Usar only() para campos específicos
- [ ] Usar agregações no banco
- [ ] Usar bulk operations
- [ ] Adicionar índices em campos filtrados
- [ ] Monitorar queries lentas
