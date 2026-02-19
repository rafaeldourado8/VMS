# Guia de Reorganização de Branches

## Estrutura Desejada
- **local**: Branch de trabalho local (atual vms-v3)
- **dev**: Branch de desenvolvimento
- **prod**: Branch de produção

## Opção 1: Script Automático (Recomendado)

Execute o script que faz tudo automaticamente:

```bash
reorganize_all_branches.bat
```

## Opção 2: Passo a Passo Manual

### 1. Commitar mudanças atuais
```bash
git add .
git commit -m "chore: consolidacao antes da reorganizacao de branches"
```

### 2. Renomear branch atual
```bash
git branch -m vms-v3 local
```

### 3. Criar novas branches
```bash
git branch dev
git branch prod
```

### 4. Deletar branches locais antigas
```bash
git branch -D alpr descart dvr-lite frontend ia-detection main mvp recording sprint-2-multi-tenant versao-1 vms-v1-mvp
```

### 5. Fazer push das novas branches
```bash
git push -u origin local
git push -u origin dev
git push -u origin prod
```

### 6. Deletar branches remotas antigas
```bash
git push origin --delete alpr
git push origin --delete dvr-lite
git push origin --delete frontend
git push origin --delete ia-detection
git push origin --delete main
git push origin --delete mvp
git push origin --delete mvp-1
git push origin --delete recording
git push origin --delete sprint-2-multi-tenant
git push origin --delete versao-1
git push origin --delete vms-v1-mvp
git push origin --delete vms-v3
```

### 7. Atualizar HEAD remoto
```bash
git remote set-head origin dev
```

### 8. Verificar resultado
```bash
git branch -a
```

## Opção 3: Scripts Separados

Se preferir fazer em etapas:

1. **Reorganizar local**: `reorganize_branches.bat`
2. **Limpar remoto**: `cleanup_remote_branches.bat`

## Verificação Final

Após a reorganização, você deve ter:

**Branches Locais:**
- local (atual)
- dev
- prod

**Branches Remotas:**
- origin/local
- origin/dev
- origin/prod

## Workflow Recomendado

- **local**: Desenvolvimento diário, experimentos
- **dev**: Merge de features testadas, ambiente de staging
- **prod**: Código em produção, apenas merges de dev testados

## Comandos Úteis

```bash
# Ver todas as branches
git branch -a

# Mudar de branch
git checkout dev

# Merge de local para dev
git checkout dev
git merge local

# Merge de dev para prod
git checkout prod
git merge dev
```
