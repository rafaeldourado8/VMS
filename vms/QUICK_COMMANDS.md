# ⚡ Comandos Rápidos - VMS Quality

## 🚀 Ativação do Ambiente

```bash
venv\Scripts\activate
```

## 🧪 Testes

```bash
# Todos os testes
run_all_tests.bat

# Módulo específico
cd src\admin && ..\..\venv\Scripts\pytest tests\unit -v

# Com coverage HTML
cd src\admin && ..\..\venv\Scripts\pytest tests\unit --cov=. --cov-report=html
```

## 📊 Análises

```bash
# Complexidade
analyze_complexity.bat

# SOLID
analyze_solid.bat

# Completa
analyze_quality.bat
```

## 🔍 Comandos Individuais

### Complexidade
```bash
venv\Scripts\radon cc src\admin -a -s
```

### SOLID
```bash
venv\Scripts\pylint src\admin --disable=C0114,C0115,C0116
```

### Segurança
```bash
venv\Scripts\bandit -r src
```

### Dead Code
```bash
venv\Scripts\vulture src --min-confidence 80
```

## 📈 Resultados Esperados

```
✅ Testes: 100% passing
✅ Coverage: >90%
✅ Complexity: A (1-5)
✅ Pylint: >8.0/10
✅ Security: 0 critical
```

## 📁 Relatórios

```
reports/
├── coverage/*/index.html
├── complexity.txt
├── pylint_*.txt
├── security.txt
└── deadcode.txt
```
