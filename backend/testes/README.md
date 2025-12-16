# 🧪 Suite de Testes GT-Vision Backend

Suite completa de testes automatizados para o backend do GT-Vision.

## 📋 Estrutura

```
testes/
├── crud/                    # Testes CRUD
│   ├── test_cameras_crud.py
│   └── test_deteccoes_crud.py
├── seguranca/              # Testes de Segurança
│   ├── test_authentication.py
│   └── test_rate_limiting.py
├── velocidade/             # Testes de Performance
│   └── test_api_performance.py
├── persistencia/           # Testes de Banco de Dados
│   └── test_database_integrity.py
├── streaming/              # Testes de Streaming
│   └── test_mediamtx_integration.py
├── carga/                  # Testes de Carga
│   ├── test_load_cameras.py
│   └── test_load_deteccoes.py
├── conftest.py             # Fixtures globais
└── README.md               # Este arquivo
```

## 🚀 Como Executar

### Pré-requisitos

✅ **Docker e Docker Compose instalados**  
✅ **Containers rodando** (`docker-compose up -d`)

### Executar Todos os Testes

```bash
# Linux/Mac
./run_tests.sh all

# Windows
run_tests.bat all

# Ou diretamente com docker-compose
docker-compose exec backend pytest testes/ -v
```

### Executar por Categoria

```bash
# CRUD
./run_tests.sh crud

# Segurança
./run_tests.sh security

# Performance
./run_tests.sh performance

# Persistência
./run_tests.sh persistence

# Streaming
./run_tests.sh streaming

# Carga
./run_tests.sh load
```

### Executar Teste Específico

```bash
# Teste específico
docker-compose exec backend pytest testes/crud/test_cameras_crud.py::TestCamerasCRUD::test_create_camera -v

# Classe de testes
docker-compose exec backend pytest testes/crud/test_cameras_crud.py::TestCamerasCRUD -v

# Com verbose
docker-compose exec backend pytest testes/crud/ -v
```

### Com Coverage

```bash
# Gerar relatório de cobertura
./run_tests.sh coverage

# Ou diretamente
docker-compose exec backend pytest testes/ --cov=apps --cov-report=html

# Ver relatório (abrir no navegador)
open backend/htmlcov/index.html
```

## 📊 Categorias de Testes

### 1. CRUD (Create, Read, Update, Delete)
- ✅ Criação de câmeras e detecções
- ✅ Listagem com paginação
- ✅ Filtros e buscas
- ✅ Atualização de registros
- ✅ Exclusão de registros

**Cobertura:** 45 testes

### 2. Segurança
- ✅ Autenticação JWT
- ✅ Autorização e permissões
- ✅ Proteção contra SQL Injection
- ✅ Proteção contra XSS
- ✅ Rate Limiting
- ✅ Token expiration

**Cobertura:** 15 testes

### 3. Performance/Velocidade
- ✅ Tempo de resposta da API (<200ms)
- ✅ Operações em massa
- ✅ Paginação eficiente
- ✅ Filtros otimizados
- ✅ Problema N+1 queries

**Cobertura:** 10 testes

### 4. Persistência
- ✅ Integridade referencial
- ✅ Constraints de unicidade
- ✅ Transações e rollback
- ✅ Cascade delete
- ✅ Validação de dados
- ✅ Concorrência

**Cobertura:** 12 testes

### 5. Streaming
- ✅ Integração com MediaMTX
- ✅ Health checks
- ✅ Métricas de streams
- ✅ Reconexão automática
- ✅ Streams concorrentes

**Cobertura:** 10 testes

### 6. Carga
- ✅ 250 câmeras simultâneas
- ✅ 1000+ detecções/segundo
- ✅ Operações concorrentes
- ✅ Carga sustentada
- ✅ Limites do sistema

**Cobertura:** 15 testes

## 📈 Métricas de Sucesso

### Performance
- API response time: **<200ms** (p95)
- Bulk operations: **>50 ops/segundo**
- Concurrent requests: **100+ simultâneas**
- Database queries: **<5 queries por request**

### Carga
- Câmeras suportadas: **250+**
- Detecções/segundo: **1000+**
- Taxa de sucesso: **>95%**
- Uptime sob carga: **>99%**

### Segurança
- Zero SQL Injection vulnerabilities
- Zero XSS vulnerabilities
- JWT validation: **100%**
- Rate limiting: **Ativo**

## 🔧 Configuração

### pytest.ini

```ini
[pytest]
DJANGO_SETTINGS_MODULE = config.settings
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --verbose
    --strict-markers
    --tb=short
    --disable-warnings
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
    load: marks tests as load tests
```

### Fixtures Disponíveis

- `api_client` - Cliente API REST
- `authenticated_client` - Cliente autenticado com JWT
- `test_user` - Usuário de teste
- `admin_user` - Usuário admin
- `test_camera` - Câmera de teste
- `multiple_cameras` - 10 câmeras para testes de carga

## 📝 Relatórios

### Coverage Report

```bash
pytest testes/ --cov=apps --cov-report=html
open htmlcov/index.html
```

### JUnit XML (CI/CD)

```bash
pytest testes/ --junitxml=test-results.xml
```

### JSON Report

```bash
pytest testes/ --json-report --json-report-file=report.json
```

## 🎯 Metas de Cobertura

- **Cobertura geral:** >80%
- **Código crítico:** >95%
- **APIs públicas:** 100%

## 🚨 Testes Críticos

Testes que **DEVEM** passar antes de deploy:

```bash
# Segurança
pytest testes/seguranca/ -v

# CRUD básico
pytest testes/crud/test_cameras_crud.py::TestCamerasCRUD::test_create_camera
pytest testes/crud/test_cameras_crud.py::TestCamerasCRUD::test_list_cameras

# Performance crítica
pytest testes/velocidade/test_api_performance.py::TestAPIPerformance::test_list_cameras_response_time
```

## 🔄 CI/CD Integration

### GitHub Actions

```yaml
- name: Run Tests
  run: |
    pytest testes/ --cov=apps --junitxml=test-results.xml
    
- name: Upload Coverage
  uses: codecov/codecov-action@v3
```

### Docker (Recomendado)

```bash
# Linux/Mac
./run_tests.sh all

# Windows
run_tests.bat all

# Ou diretamente
docker-compose exec backend pytest testes/ -v

# Com coverage
docker-compose exec backend pytest testes/ --cov=apps --cov-report=html
```

## 📚 Documentação Adicional

- [Pytest Documentation](https://docs.pytest.org/)
- [Django Testing](https://docs.djangoproject.com/en/5.0/topics/testing/)
- [DRF Testing](https://www.django-rest-framework.org/api-guide/testing/)

## 🤝 Contribuindo

Ao adicionar novos testes:

1. Seguir estrutura de pastas existente
2. Usar fixtures do `conftest.py`
3. Nomear testes descritivamente: `test_<acao>_<resultado_esperado>`
4. Adicionar docstrings
5. Manter cobertura >80%

## ✅ Checklist de Testes

Antes de fazer commit:

- [ ] Todos os testes passam
- [ ] Cobertura >80%
- [ ] Sem warnings
- [ ] Testes de segurança passam
- [ ] Performance dentro dos limites
- [ ] Documentação atualizada
