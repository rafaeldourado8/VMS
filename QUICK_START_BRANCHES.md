# Reorganização de Branches - Guia Rápido

## 🚀 Método Recomendado (2 passos)

### Passo 1: Reorganizar
```bash
reorganize_simple.bat
```
Isso vai:
- Commitar mudanças
- Renomear branch atual para `local`
- Criar `dev` e `prod`
- Fazer push

### Passo 2: Limpar (OPCIONAL)
```bash
delete_old_branches.bat
```
Isso vai deletar todas as branches antigas (local e remoto)

## ⚠️ Se der erro

Execute os comandos manualmente:

```bash
# 1. Commit
git add .
git commit -m "reorganizacao"

# 2. Renomear
git branch -m local

# 3. Criar
git branch dev
git branch prod

# 4. Push
git push -u origin local
git push origin dev
git push origin prod

# 5. Deletar antigas (CUIDADO!)
git branch -D vms-v3 alpr main mvp
git push origin --delete vms-v3 alpr main mvp
```

## ✅ Resultado Final

Você terá:
- `local` - trabalho diário
- `dev` - desenvolvimento
- `prod` - produção
