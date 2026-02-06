# 🐛 MediaMTX - Bugs e Soluções

Documentação de problemas encontrados durante integração do MediaMTX v1.16.0

---

## BUG #1: recordPath com variável incorreta

**Data**: 2026-02-06  
**Severidade**: 🔴 Crítica  
**Status**: ✅ Resolvido

### Sintoma
```
ERR [API] 'recordPath' must contain %path
```

### Causa
Uso de `%path` (sintaxe strftime) em vez de `$path` (variável MediaMTX)

### Código Incorreto
```yaml
recordPath: /recordings/%path/%Y-%m-%d/%H.mp4
```

### Solução
```yaml
recordPath: /recordings/$path/%Y-%m-%d/%H.mp4
```

### Lição Aprendida
- MediaMTX usa `$variable` para variáveis próprias (ex: `$path`)
- Usa `%format` apenas para data/hora (ex: `%Y`, `%H`)

---

## BUG #2: recordPath sem variáveis temporais obrigatórias

**Data**: 2026-02-06  
**Severidade**: 🔴 Crítica  
**Status**: ✅ Resolvido

### Sintoma
```
ERR [API] 'recordPath' must contain either %s or %Y %m %d %H %M %S
```

### Causa
Tentativa de usar apenas `%H.mp4` sem incluir minutos/segundos

### Código Incorreto
```yaml
recordPath: /recordings/$path/%Y-%m-%d/%H.mp4
```

### Solução
```yaml
recordPath: /recordings/$path/%Y-%m-%d/%H-%M-%S.mp4
```

### Lição Aprendida
MediaMTX exige granularidade mínima de segundos no path para evitar sobrescrita de arquivos

---

## BUG #3: recordPath sem %f em segmentação

**Data**: 2026-02-06  
**Severidade**: 🔴 Crítica  
**Status**: ✅ Resolvido

### Sintoma
```
ERR [API] 'recordPath' must contain %f
```

### Causa
Quando `recordSegmentDuration` está configurado, MediaMTX exige `%f` (frame/fragment number) para diferenciar segmentos

### Código Incorreto
```yaml
recordPath: /recordings/$path/%Y-%m-%d/%H-%M-%S.mp4
recordSegmentDuration: 1h
```

### Solução
```yaml
recordPath: /recordings/$path/%Y-%m-%d/%H-%M-%S-%f.mp4
recordSegmentDuration: 1h
```

### Lição Aprendida
- `%f` é obrigatório quando usa segmentação
- Gera arquivos como: `12-15-58-000001.mp4`, `12-15-58-000002.mp4`

---

## BUG #4: Path não configurado (404)

**Data**: 2026-02-06  
**Severidade**: 🟡 Média  
**Status**: ✅ Resolvido

### Sintoma
```
ERR [RTSP] path 'cam_9' is not configured
index.m3u8 404 Not Found
```

### Causa
Câmera não foi provisionada via API do MediaMTX antes de tentar acessar HLS

### Solução
1. Provisionar câmera via API:
```bash
curl -X POST http://mediamtx:9997/v3/config/paths/add/cam_9 \
  -u mediamtx_api_user:password \
  -H "Content-Type: application/json" \
  -d '{
    "source": "rtsp://...",
    "sourceOnDemand": false,
    "record": true,
    "recordPath": "/recordings/$path/%Y-%m-%d/%H-%M-%S-%f.mp4"
  }'
```

2. Verificar se path existe:
```bash
curl http://mediamtx:9997/v3/paths/get/cam_9 -u user:pass
```

### Lição Aprendida
- Paths devem ser criados via API antes do uso
- `sourceOnDemand: false` requer fonte RTSP ativa para path ficar "ready"

---

## BUG #5: Arquivo .mp4.mp4 duplicado

**Data**: 2026-02-06  
**Severidade**: 🟢 Baixa  
**Status**: ✅ Resolvido

### Sintoma
Arquivos gerados com extensão duplicada: `12-15-58-860268.mp4.mp4`

### Causa
Interpolação Python adicionando `.mp4` + template MediaMTX já tinha `.mp4`

### Código Incorreto (Python)
```python
"recordPath": f"/recordings/{stream_path}/%Y-%m-%d/%H-%M-%S-%f.mp4"
```

### Solução
```python
"recordPath": "/recordings/%path/%Y-%m-%d/%H-%M-%S-%f.mp4"
```

### Lição Aprendida
Usar variável `%path` do MediaMTX em vez de interpolar com Python

---

## BUG #6: Container não recarrega código após alteração

**Data**: 2026-02-06  
**Severidade**: 🟡 Média  
**Status**: ✅ Resolvido

### Sintoma
Alterações no código Python não refletem após `docker restart`

### Causa
Dockerfile usa `COPY . .` - código é copiado durante build, não em runtime

### Solução
```bash
# Rebuildar imagem
docker-compose build streaming

# Recriar container
docker-compose up -d streaming
```

### Alternativa (Dev)
Usar volume mount no docker-compose.yml:
```yaml
volumes:
  - ./services/streaming:/app
```

### Lição Aprendida
- Em produção: sempre rebuild após alteração de código
- Em dev: usar volumes para hot-reload

---

## Checklist de Validação

Antes de provisionar câmeras, verificar:

- [ ] `recordPath` usa `$path` (não `%path`)
- [ ] `recordPath` contém `%Y %m %d %H %M %S`
- [ ] `recordPath` contém `%f` se usar `recordSegmentDuration`
- [ ] Path provisionado via API antes de acessar HLS
- [ ] Container rebuilded após alteração de código
- [ ] Fonte RTSP acessível se `sourceOnDemand: false`

---

## Comandos Úteis de Debug

```bash
# Verificar paths configurados
curl -s http://localhost:9997/v3/paths/list \
  -u mediamtx_api_user:GtV!sionMed1aMTX$2025 | python -m json.tool

# Verificar status de uma câmera
curl -s http://localhost:9997/v3/paths/get/cam_1 \
  -u mediamtx_api_user:GtV!sionMed1aMTX$2025 | python -m json.tool

# Verificar logs de gravação
docker logs gtvision_mediamtx 2>&1 | grep -i record

# Listar arquivos gravados
docker exec gtvision_mediamtx ls -lh /recordings/cam_1/$(date +%Y-%m-%d)/

# Verificar integridade de arquivo
docker exec gtvision_mediamtx ffprobe /recordings/cam_1/2026-02-06/12-00-00-000001.mp4
```

---

## Referências

- [MediaMTX Documentation](https://github.com/bluenviron/mediamtx)
- [MediaMTX API Reference](https://github.com/bluenviron/mediamtx/blob/main/apidocs/openapi.yaml)
- Versão testada: MediaMTX v1.16.0
