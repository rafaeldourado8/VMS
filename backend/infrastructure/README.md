# Infrastructure Layer

## 📁 Estrutura

```
infrastructure/
├── persistence/django/
│   ├── models/           # Django Models
│   ├── repositories/     # Implementações concretas dos repositórios
│   └── migrations/       # Migrações Django
├── messaging/celery/     # Tasks Celery
└── external_services/    # Clientes HTTP
```

## 🔄 Mappers

Convertem entre entidades de domínio e models Django:

- **CameraMapper**: Camera ↔ CameraModel
- **DetectionMapper**: Detection ↔ DetectionModel

## 💾 Repositórios

Implementações concretas das interfaces de domínio:

- **DjangoCameraRepository**: Usa CameraModel
- **DjangoDetectionRepository**: Usa DetectionModel

## 🔌 Compatibilidade

Models usam `db_table` para manter compatibilidade com tabelas existentes:
- `CameraModel` → `cameras_camera`
- `DetectionModel` → `deteccoes_deteccao`

## 🧪 Testes

Testes de integração em `tests/integration/`:
- Usam banco de dados real (SQLite em memória)
- Marcados com `@pytest.mark.django_db`
