# Correção Erro 502 - Clips

## Problema
Erro 502 (Bad Gateway) ao acessar endpoints de clips

## Causa
- Import do `httpx` causando erro no backend
- Dependência desnecessária do serviço de clips para servir vídeos

## Solução

### 1. Simplificado endpoint de vídeo
- Removida dependência do `httpx`
- Busca direta do arquivo no filesystem
- Múltiplos paths possíveis para encontrar o arquivo

### 2. Adicionado campo `status` no serializer
- Agora retorna o status do clip na listagem

### 3. Simplificado endpoint de status
- Retorna status direto do banco de dados

## Arquivos Alterados

- `backend/apps/clips/views.py` - Simplificado endpoints
- `backend/apps/clips/serializers.py` - Adicionado campo status

## Testar

```bash
docker-compose restart backend
```

Depois acesse a página de clips no frontend.
