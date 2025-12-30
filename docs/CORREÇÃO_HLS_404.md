# Correção do Erro 404 no HLS (index.m3u8)

## Problema Identificado

Quando uma nova câmera era adicionada no frontend, ocorriam erros 404 ao tentar acessar o arquivo `index.m3u8`:

```
index.m3u8	404	xhr	VideoPlayer.tsx:141	0,2 kB	5 ms
index.m3u8	404	xhr	VideoPlayer.tsx:52	0,0 kB	12 ms
```

## Causa Raiz

**Incompatibilidade de nomenclatura entre os componentes:**

1. **Frontend** (`api.ts`): Gerava URLs como `/hls/camera${cameraId}/index.m3u8`
2. **Streaming Service** (`main.py`): Criava paths como `cam_${camera_id}`
3. **HAProxy** (`haproxy.cfg`): Roteamento inconsistente

## Correções Aplicadas

### 1. Frontend - Correção da URL HLS
**Arquivo:** `frontend/src/services/api.ts`
```typescript
// ANTES
getHlsUrl(cameraId: number): string {
  return `/hls/camera${cameraId}/index.m3u8`
}

// DEPOIS
getHlsUrl(cameraId: number): string {
  return `/hls/cam_${cameraId}/index.m3u8`
}
```

### 2. HAProxy - Correção do Roteamento Legacy
**Arquivo:** `haproxy/haproxy.cfg`
```haproxy
# ANTES
http-request replace-path /streaming/hls/cam_([0-9]+)/(.*) /camera\\1/\\2

# DEPOIS  
http-request replace-path /streaming/hls/cam_([0-9]+)/(.*) /cam_\\1/\\2
```

### 3. Streaming Service - URLs Relativas
**Arquivo:** `services/streaming/main.py`
```python
# ANTES
hls_url=f"{settings.mediamtx_hls_url}/{stream_path}/index.m3u8"

# DEPOIS
hls_url=f"/hls/{stream_path}/index.m3u8"
```

### 4. MediaMTX - Configurações de Estabilidade
**Arquivo:** `mediamtx.yml`
```yaml
pathDefaults:
  # Adicionadas configurações de timeout e retry
  sourceTimeout: 10s
  sourceRetry: yes
  sourceRetryDelay: 5s
```

## Fluxo Corrigido

1. **Usuário cria câmera** no frontend
2. **Backend** chama Streaming Service para provisionar
3. **Streaming Service** cria path `cam_123` no MediaMTX
4. **Frontend** gera URL `/hls/cam_123/index.m3u8`
5. **HAProxy** roteia para MediaMTX corretamente
6. **MediaMTX** serve o HLS playlist

## Teste da Correção

Execute o script de teste:
```bash
python test_camera_streaming.py
```

O script irá:
- ✅ Provisionar uma câmera de teste
- ✅ Verificar acesso direto ao MediaMTX
- ✅ Verificar acesso via HAProxy
- ✅ Validar o playlist HLS
- ✅ Limpar recursos de teste

## Verificação Manual

1. **Criar nova câmera** no frontend
2. **Verificar logs** do Streaming Service:
   ```
   📹 Stream provisionado: cam_123 -> /hls/cam_123/index.m3u8
   ```
3. **Testar URL** diretamente no browser:
   ```
   http://localhost/hls/cam_123/index.m3u8
   ```

## Prevenção de Problemas Futuros

- ✅ Nomenclatura consistente (`cam_` em todos os componentes)
- ✅ URLs relativas para flexibilidade de roteamento
- ✅ Configurações de retry no MediaMTX
- ✅ Script de teste automatizado
- ✅ Documentação clara do fluxo

## Monitoramento

Para monitorar se o problema foi resolvido:

1. **Logs do HAProxy**: `http://localhost:8404/stats`
2. **Stats do Streaming**: `http://localhost:8001/stats`
3. **API do MediaMTX**: `http://localhost:9997/v3/paths/list`