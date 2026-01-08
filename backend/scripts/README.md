# 🔧 Scripts VMS Backend

## Scripts Disponíveis

### Organização e Otimização
- `organize_imports.py` - Organiza imports em todos os arquivos Python
- `optimize_indexes.py` - Cria índices otimizados no banco de dados

### Testes
- `test_fase6.py` - Testes da Fase 6 (Support & Clips)
- `test_e2e_staging.py` - Testes End-to-End para staging
- `locustfile.py` - Testes de carga com Locust

### Análise
- `analyze_cc.sh` - Análise de complexidade ciclomática

### Utilitários
- `wait_for_db.py` - Aguarda banco de dados estar pronto

## Como Usar

```bash
# Organizar imports
python scripts/organize_imports.py

# Otimizar índices
python scripts/optimize_indexes.py

# Testes E2E
python scripts/test_e2e_staging.py

# Testes de carga
locust -f scripts/locustfile.py
```