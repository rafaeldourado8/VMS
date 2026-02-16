# Página de Gerenciamento IAM

## 📋 Visão Geral

Página completa de gerenciamento de acesso estilo AWS IAM com 3 abas principais:
- **Usuários**: CRUD de usuários com roles e permissões
- **Permissões**: Visualização de todas as permissões disponíveis
- **Regras**: Políticas de acesso baseadas em condições

## 🎯 Funcionalidades

### 1. Gerenciamento de Usuários
- Criar, editar e deletar usuários
- Definir roles: Admin, Operator, Viewer
- Atribuir permissões granulares
- Ativar/desativar usuários
- Visualização em tabela com filtros

### 2. Permissões
- Visualização de todas as permissões do sistema
- Agrupadas por recurso (cameras, recordings, detections, etc)
- Descrição detalhada de cada permissão
- ID da permissão para referência

### 3. Regras de Acesso
- Criar políticas baseadas em condições JSON
- Definir ações (allow, deny, log)
- Ativar/desativar regras
- Editor JSON para condições complexas

## 🔐 Permissões Disponíveis

### Câmeras
- `cameras.view` - Visualizar câmeras
- `cameras.create` - Criar câmeras
- `cameras.edit` - Editar câmeras
- `cameras.delete` - Deletar câmeras

### Gravações
- `recordings.view` - Visualizar gravações
- `recordings.download` - Baixar gravações
- `recordings.delete` - Deletar gravações

### Detecções
- `detections.view` - Visualizar detecções LPR

### Sistema
- `users.manage` - Gerenciar usuários
- `settings.manage` - Gerenciar configurações

## 👥 Roles

### Admin
- Acesso total ao sistema
- Pode gerenciar usuários e permissões
- Pode criar e editar regras

### Operator
- Pode gerenciar câmeras
- Pode visualizar e baixar gravações
- Pode visualizar detecções

### Viewer
- Apenas visualização
- Não pode modificar nada

## 📝 Exemplo de Regra

```json
{
  "name": "Operadores podem editar câmeras",
  "description": "Permite operadores editarem câmeras durante horário comercial",
  "conditions": {
    "role": "operator",
    "resource": "cameras",
    "time": {
      "start": "08:00",
      "end": "18:00"
    }
  },
  "actions": ["allow", "log"],
  "is_active": true
}
```

## 🚀 Acesso

```
URL: /settings/iam
```

## 📦 APIs Necessárias (Backend)

```python
# Usuários
GET    /api/users/              # Lista usuários
POST   /api/users/              # Criar usuário
PUT    /api/users/{id}/         # Atualizar usuário
DELETE /api/users/{id}/         # Deletar usuário

# Regras
GET    /api/iam/rules/          # Lista regras
POST   /api/iam/rules/          # Criar regra
PUT    /api/iam/rules/{id}/     # Atualizar regra
DELETE /api/iam/rules/{id}/     # Deletar regra
```

## 🎨 Interface

### Usuários Tab
- Tabela com nome, email, role, status e permissões
- Botão "Novo Usuário" no topo
- Ações: Editar e Deletar por linha
- Modal para criar/editar com formulário completo

### Permissões Tab
- Cards agrupados por recurso
- Cada permissão mostra nome, descrição e ID
- Ícone de chave para identificação visual

### Regras Tab
- Cards com nome, descrição e status
- Visualização de condições em JSON
- Tags para ações
- Modal com editor JSON para condições

## 🔧 Integração com Backend

O frontend está pronto. Backend precisa implementar:

1. **User Model** com campos:
   - name, email, password (hash)
   - role (admin/operator/viewer)
   - permissions (JSONField ou ManyToMany)
   - is_active

2. **Rule Model** com campos:
   - name, description
   - conditions (JSONField)
   - actions (JSONField)
   - is_active

3. **Middleware de Permissões**:
   - Verificar permissões em cada request
   - Avaliar regras baseadas em condições
   - Logar acessos negados

## 📊 Exemplo de Uso

1. Admin acessa `/settings/iam`
2. Cria novo usuário "João" com role "Operator"
3. Atribui permissões: cameras.view, cameras.edit, recordings.view
4. Cria regra: "Operadores só editam câmeras das 8h às 18h"
5. João faz login e só consegue editar câmeras no horário permitido

## 🎯 Benefícios

✅ Controle granular de acesso  
✅ Auditoria completa de permissões  
✅ Regras dinâmicas baseadas em contexto  
✅ Interface intuitiva estilo AWS  
✅ Escalável para múltiplos usuários  
✅ Segurança em camadas  
