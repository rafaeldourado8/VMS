# Segurança de Gravações - TODO

## Problema Identificado
O endpoint `/recordings/` está exposto sem autenticação. Qualquer pessoa com acesso à rede pode acessar vídeos diretamente.

## Risco
- **Severidade**: ALTA
- **Impacto**: Vazamento de vídeos de vigilância
- **Exposição**: Rede local (porta 80)

## Solução Proposta (Para Implementação Futura)

### Opção 1: Nginx auth_request (Tentada - Falhou com 500)
```nginx
location /recordings/ {
    auth_request /auth/validate;
    # ...
}
```
**Problema**: Erro 500 ao validar token

### Opção 2: Proxy via Backend Django (RECOMENDADO)
Ao invés de servir diretamente via Nginx, criar endpoint Django:

```python
# apps/recordings/views.py
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def serve_recording(request, camera_id, date, filename):
    # Validar permissões do usuário
    # Servir arquivo via FileResponse com X-Accel-Redirect
    file_path = f"/recordings/camera_{camera_id}/{date}/{filename}"
    response = FileResponse(open(file_path, 'rb'))
    return response
```

**Vantagens**:
- Controle fino de permissões (usuário só vê suas câmeras)
- Logs de acesso
- Rate limiting
- Auditoria

### Opção 3: Signed URLs (Temporárias)
Gerar URLs assinadas com expiração:
```python
def generate_signed_url(file_path, expires_in=3600):
    signature = hmac.new(SECRET_KEY, f"{file_path}:{expires}".encode()).hexdigest()
    return f"/recordings/{file_path}?expires={expires}&sig={signature}"
```

## Mitigação Temporária
- Firewall: Bloquear porta 80 externamente
- VPN: Acesso apenas via VPN corporativa
- Network segmentation: Isolar VMS em VLAN separada

## Implementação Recomendada
1. Criar endpoint Django: `/api/recordings/serve/<path>`
2. Validar JWT + permissões de câmera
3. Usar X-Accel-Redirect do Nginx para performance
4. Adicionar rate limiting (max 10 vídeos/min por usuário)

## Prioridade
**ALTA** - Implementar antes de produção
