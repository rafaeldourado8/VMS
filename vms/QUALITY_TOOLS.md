# 🧪 Ferramentas de Análise de Qualidade

## 📦 Ambiente Virtual

### Criação
```bash
py -m venv venv
```

### Ativação
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### Instalação de Dependências
```bash
pip install -r requirements-quality.txt
```

---

## 🛠️ Ferramentas Instaladas

### 1. **Pytest** - Testes Unitários
**Propósito:** Framework de testes Python

**Uso:**
```bash
# Rodar todos os testes
pytest

# Com coverage
pytest --cov=. --cov-report=html

# Verbose
pytest -v
```

**Plugins:**
- `pytest-cov` - Coverage
- `pytest-mock` - Mocking
- `pytest-html` - Relatórios HTML

---

### 2. **Radon** - Complexidade Ciclomática
**Propósito:** Medir complexidade do código

**Uso:**
```bash
# Complexidade ciclomática
radon cc src -a -s

# Maintainability Index
radon mi src -s

# Raw metrics
radon raw src -s
```

**Escala:**
- **A** (1-5): Baixa complexidade ✅
- **B** (6-10): Média complexidade
- **C** (11-20): Alta complexidade
- **D** (21-50): Muito alta
- **F** (>50): Crítica ❌

---

### 3. **Pylint** - Análise SOLID
**Propósito:** Linting + análise de princípios SOLID

**Uso:**
```bash
# Análise completa
pylint src/admin

# Desabilitar warnings específicos
pylint src/admin --disable=C0114,C0115,C0116

# Gerar relatório
pylint src/admin --output-format=text > report.txt
```

**Verifica:**
- ✅ Single Responsibility Principle
- ✅ Open/Closed Principle
- ✅ Liskov Substitution Principle
- ✅ Interface Segregation Principle
- ✅ Dependency Inversion Principle

---

### 4. **Flake8** - Style Guide
**Propósito:** PEP 8 compliance

**Uso:**
```bash
# Verificar estilo
flake8 src

# Com configuração
flake8 src --max-line-length=120
```

---

### 5. **MyPy** - Type Checking
**Propósito:** Verificação de tipos estáticos

**Uso:**
```bash
# Type checking
mypy src/admin

# Strict mode
mypy src/admin --strict
```

---

### 6. **Bandit** - Análise de Segurança
**Propósito:** Detectar vulnerabilidades de segurança

**Uso:**
```bash
# Análise de segurança
bandit -r src

# Gerar relatório
bandit -r src -f txt -o security.txt
```

**Detecta:**
- SQL Injection
- Hardcoded passwords
- Insecure functions
- Weak cryptography

---

### 7. **Vulture** - Dead Code Detection
**Propósito:** Encontrar código não utilizado

**Uso:**
```bash
# Detectar dead code
vulture src

# Com confiança mínima
vulture src --min-confidence 80
```

---

### 8. **McCabe** - Complexity
**Propósito:** Medir complexidade ciclomática

**Uso:**
```bash
# Integrado com flake8
flake8 src --max-complexity=10
```

---

## 📊 Scripts de Análise

### 1. Testes com Coverage
```bash
run_all_tests.bat
```
Executa todos os testes com coverage report.

### 2. Complexidade Ciclomática
```bash
analyze_complexity.bat
```
Analisa complexidade de todos os módulos.

### 3. Análise SOLID
```bash
analyze_solid.bat
```
Verifica princípios SOLID com Pylint.

### 4. Análise Completa
```bash
analyze_quality.bat
```
Executa todas as análises e gera relatórios.

---

## 📁 Estrutura de Relatórios

```
reports/
├── coverage/
│   ├── admin/index.html
│   ├── cidades/index.html
│   ├── cameras/index.html
│   ├── streaming/index.html
│   └── lpr/index.html
├── complexity.txt
├── pylint_admin.txt
├── pylint_cidades.txt
├── pylint_cameras.txt
├── pylint_streaming.txt
├── pylint_lpr.txt
├── security.txt
└── deadcode.txt
```

---

## 🎯 Métricas de Qualidade

### Testes
- **Coverage:** >90% ✅
- **Testes passando:** 100%
- **Tempo:** <5s

### Complexidade
- **Média:** A (1-5) ✅
- **Máxima:** B (6-10)
- **Crítica:** 0

### SOLID
- **Score Pylint:** >8.0/10 ✅
- **Warnings:** <10
- **Errors:** 0

### Segurança
- **Issues críticos:** 0 ✅
- **Issues médios:** <5
- **Issues baixos:** <10

---

## 🚀 Workflow de Qualidade

### 1. Antes de Commit
```bash
# Rodar testes
pytest

# Verificar complexidade
radon cc src -a -s

# Verificar estilo
flake8 src
```

### 2. Antes de PR
```bash
# Análise completa
analyze_quality.bat

# Verificar relatórios
# - Coverage >90%
# - Complexidade A
# - Pylint >8.0
# - Sem issues de segurança
```

### 3. CI/CD
```yaml
# .github/workflows/quality.yml
- name: Run tests
  run: pytest --cov=. --cov-report=xml

- name: Check complexity
  run: radon cc src -a -s

- name: Lint
  run: pylint src

- name: Security
  run: bandit -r src
```

---

## 📚 Documentação

### Pytest
- https://docs.pytest.org/

### Radon
- https://radon.readthedocs.io/

### Pylint
- https://pylint.pycqa.org/

### Bandit
- https://bandit.readthedocs.io/

### Vulture
- https://github.com/jendrikseipp/vulture

---

## ✅ Checklist de Qualidade

### Código
- [ ] Testes >90% coverage
- [ ] Complexidade A (1-5)
- [ ] Pylint score >8.0
- [ ] Sem dead code
- [ ] Type hints em tudo

### Arquitetura
- [ ] Domain puro (sem frameworks)
- [ ] Interfaces para dependências
- [ ] Use Cases isolados
- [ ] SOLID respeitado

### Segurança
- [ ] Sem hardcoded secrets
- [ ] Sem SQL injection
- [ ] Sem weak crypto
- [ ] Inputs validados

---

**Criado:** 2024  
**Versão:** 1.0.0  
**Projeto:** VMS
