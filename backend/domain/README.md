# Backend VMS - Arquitetura DDD

## 📁 Estrutura de Diretórios

```
backend/
├── domain/              # Camada de Domínio (lógica de negócio pura)
├── application/         # Camada de Aplicação (use cases, CQRS)
├── infrastructure/      # Camada de Infraestrutura (Django, Celery, APIs externas)
├── apps/               # Apps Django legados (em migração)
└── tests/              # Testes unitários e de integração
```

## 🎯 Camadas

### Domain Layer
Contém a lógica de negócio pura, sem dependências de frameworks.

- **entities/**: Entidades de domínio com comportamento
- **value_objects/**: Objetos de valor imutáveis
- **repositories/**: Interfaces de repositórios (abstrações)
- **services/**: Serviços de domínio
- **exceptions.py**: Exceções de domínio

### Application Layer
Orquestra os use cases usando CQRS pattern.

- **commands/**: DTOs de comandos (write operations)
- **queries/**: DTOs de queries (read operations)
- **handlers/**: Handlers que executam use cases

### Infrastructure Layer
Implementações concretas de infraestrutura.

- **persistence/django/**: Models Django e repositórios concretos
- **messaging/celery/**: Tasks Celery
- **external_services/**: Clientes HTTP para APIs externas

## 🧪 Testes

```bash
# Executar todos os testes
pytest

# Executar com cobertura
pytest --cov

# Analisar complexidade ciclomática
bash analyze_cc.sh
```

## 📊 Métricas

- **Cobertura**: > 80%
- **CC**: < 10 por método
- **Type hints**: 100%

## 🚀 Status

**Fase atual**: Setup inicial completo ✅

**Próximo**: Implementar Monitoring Context (domain layer)
