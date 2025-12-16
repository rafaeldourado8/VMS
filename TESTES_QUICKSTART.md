# 🚀 Testes - Guia Rápido (Docker)

## ⚡ Início Rápido

### 1. Certifique-se que os containers estão rodando

```bash
docker-compose up -d
```

### 2. Execute os testes

**Linux/Mac:**
```bash
./run_tests.sh all
```

**Windows:**
```bash
run_tests.bat all
```

## 📋 Comandos Principais

### Todos os Testes
```bash
./run_tests.sh all
```

### Por Categoria
```bash
./run_tests.sh crud         # Testes CRUD
./run_tests.sh security     # Testes de Segurança
./run_tests.sh performance  # Testes de Performance
./run_tests.sh load         # Testes de Carga
```

### Testes Rápidos (sem carga)
```bash
./run_tests.sh quick
```

### Testes Críticos (pré-deploy)
```bash
./run_tests.sh critical
```

### Com Coverage
```bash
./run_tests.sh coverage
```

## 🎯 Comandos Docker Diretos

### Executar todos os testes
```bash
docker-compose exec backend pytest testes/ -v
```

### Executar categoria específica
```bash
docker-compose exec backend pytest testes/crud/ -v
docker-compose exec backend pytest testes/seguranca/ -v
```

### Executar teste específico
```bash
docker-compose exec backend pytest testes/crud/test_cameras_crud.py::TestCamerasCRUD::test_create_camera -v
```

### Com coverage
```bash
docker-compose exec backend pytest testes/ --cov=apps --cov-report=html --cov-report=term
```

### Ver relatório de coverage
```bash
# O relatório é gerado em backend/htmlcov/index.html
# Abra no navegador
```

## 📊 Estrutura dos Testes

```
testes/
├── crud/           # 45 testes - CRUD de câmeras e detecções
├── seguranca/      # 15 testes - JWT, SQL Injection, XSS
├── velocidade/     # 10 testes - Performance da API
├── persistencia/   # 12 testes - Integridade do banco
├── streaming/      # 10 testes - Integração MediaMTX
└── carga/          # 15 testes - Carga e limites
```

**Total: 107 testes**

## ✅ Checklist Pré-Deploy

Antes de fazer deploy, execute:

```bash
# 1. Testes críticos
./run_tests.sh critical

# 2. Testes de segurança
./run_tests.sh security

# 3. Coverage (deve ser >80%)
./run_tests.sh coverage
```

## 🐛 Troubleshooting

### Erro: "No module named pytest"
**Solução:** As dependências já estão no `requirements.txt`. Reconstrua o container:
```bash
docker-compose build backend
docker-compose up -d backend
```

### Erro: "Database not found"
**Solução:** Os testes usam SQLite em memória. Certifique-se que o container está rodando:
```bash
docker-compose ps
docker-compose up -d backend
```

### Testes lentos
**Solução:** Use testes rápidos ou paralelize:
```bash
./run_tests.sh quick
# ou
docker-compose exec backend pytest testes/ -n auto
```

### Coverage não gera relatório
**Solução:** Verifique se o diretório existe:
```bash
docker-compose exec backend ls -la htmlcov/
```

## 📚 Documentação Completa

Para mais detalhes, consulte:
- `testes/README.md` - Documentação completa
- `testes/TESTS_SUMMARY.md` - Resumo da implementação

## 🎉 Pronto!

Agora você pode executar todos os testes via Docker sem precisar instalar nada localmente!

```bash
# Teste agora
./run_tests.sh all
```
