# Como Remover Secrets do Código

## Problema

Credenciais hardcoded no código podem ser expostas no repositório Git.

## Identificar Secrets

```bash
# Buscar possíveis secrets
grep -r "password" .
grep -r "api_key" .
grep -r "secret" .
```

## Correções

### 1. Mover para Variáveis de Ambiente
```python
# ❌ HARDCODED
DATABASE_PASSWORD = "mypassword123"
API_KEY = "sk-1234567890"

# ✅ VARIÁVEIS DE AMBIENTE
import os
DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD')
API_KEY = os.getenv('API_KEY')
```

### 2. Usar Arquivo .env
```bash
# .env
DATABASE_PASSWORD=mypassword123
API_KEY=sk-1234567890
```

```python
# settings.py
from dotenv import load_dotenv
load_dotenv()

DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD')
```

### 3. Adicionar .env ao .gitignore
```bash
echo ".env" >> .gitignore
```

### 4. Rotacionar Credenciais Expostas
- Trocar todas as senhas que foram commitadas
- Revogar API keys expostas
- Gerar novas credenciais

## Checklist

- [ ] Remover secrets do código
- [ ] Criar arquivo .env
- [ ] Adicionar .env ao .gitignore
- [ ] Rotacionar credenciais expostas
- [ ] Verificar histórico do Git
- [ ] Usar AWS Secrets Manager em produção
