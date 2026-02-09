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

## BUG #7: Drift entre gravação e tempo absoluto

**Data**: 2026-02-06  
**Severidade**: 🟡 Média  
**Status**: ⚠️ Monitorar

### Sintoma
```
ERR [path cam_3] [recorder] detected drift between recording duration and absolute time, resetting
WAR [path cam_3] [RTSP source] 2060 RTP packets lost
```

### Causa
- Perda de pacotes RTP na rede
- Câmera com transmissão instável
- Latência de rede alta
- Buffer overflow

### Impacto
- Gravação é resetada (cria novo arquivo)
- Possível gap de alguns segundos no vídeo
- Não afeta estabilidade do sistema

### Solução Automática
MediaMTX detecta e reseta automaticamente. Nenhuma ação necessária.

### Mitigação
```yaml
# Aumentar buffers UDP no mediamtx.yml
rtspUDPReadBufferSize: 131072  # 128KB (padrão: 65536)
rtpUDPReadBufferSize: 131072   # 128KB

# Forçar TCP (mais estável, porém mais lento)
rtspTransport: tcp
```

### Monitoramento
```bash
# Contar ocorrências de drift
docker logs gtvision_mediamtx 2>&1 | grep -c "detected drift"

# Verificar perda de pacotes por câmera
docker logs gtvision_mediamtx 2>&1 | grep "packets lost" | tail -20
```

### Quando se Preocupar
- ✅ 1-5 drifts por dia: Normal (rede/câmera instável)
- ⚠️ 10+ drifts por hora: Investigar rede/câmera
- 🔴 Drift contínuo: Câmera com problema grave

### Lição Aprendida
- Drift é esperado em redes não ideais
- MediaMTX lida automaticamente
- Usar TCP se drift for frequente
- Monitorar logs para identificar câmeras problemáticas

---

## Checklist de Validação

Antes de provisionar câmeras, verificar:

- [ ] `recordPath` usa `$path` (não `%path`)
- [ ] `recordPath` contém `%Y %m %d %H %M %S`
- [ ] `recordPath` contém `%f` se usar `recordSegmentDuration`
- [ ] Path provisionado via API antes de acessar HLS
- [ ] Container rebuilded após alteração de código
- [ ] Fonte RTSP acessível se `sourceOnDemand: false`
- [ ] Monitorar drift em logs (< 10/hora por câmera)

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

# Monitorar drift e perda de pacotes
docker logs -f gtvision_mediamtx 2>&1 | grep -E "drift|packets lost"
```

---

## Referências

- [MediaMTX Documentation](https://github.com/bluenviron/mediamtx)
- [MediaMTX API Reference](https://github.com/bluenviron/mediamtx/blob/main/apidocs/openapi.yaml)
- Versão testada: MediaMTX v1.16.0


---

## BUG #8: MediaMTX crash - integer divide by zero

**Data**: 2026-02-06  
**Severidade**: 🔴 CRÍTICA  
**Status**: ⚠️ Bug upstream (gortsplib v5.3.0)

### Sintoma
```
panic: runtime error: integer divide by zero

goroutine 347 [running]:
github.com/bluenviron/gortsplib/v5/pkg/rtpreceiver.(*Receiver).report
```

Container MediaMTX crasha completamente e para de responder.

### Causa
Bug no `gortsplib` ao calcular estatísticas RTP quando:
- Câmera envia pacotes RTP com timestamps inválidos
- Divisão por zero ao calcular taxa de perda de pacotes
- Ocorre principalmente com câmeras de baixa qualidade ou firmware antigo

### Impacto
- 🔴 MediaMTX para completamente
- 🔴 Todas as câmeras ficam offline
- 🔴 Gravações são interrompidas
- 🔴 HLS retorna 503

### Solução Imediata
```bash
# 1. Reiniciar MediaMTX
docker restart gtvision_mediamtx

# 2. Identificar câmera problemática nos logs
docker logs gtvision_mediamtx 2>&1 | findstr /C:"panic" /B

# 3. Remover câmera problemática
curl -X DELETE http://localhost:8001/cameras/{camera_id}
```

### Workaround
Desabilitar câmera problemática ou usar TCP em vez de UDP:

```python
# No streaming service, forçar TCP para câmeras problemáticas
config = {
    "source": rtsp_url,
    "rtspTransport": "tcp",  # TCP é mais estável
    "sourceProtocol": "tcp"
}
```

### Monitoramento
```bash
# Verificar se MediaMTX está rodando
docker ps | findstr mediamtx

# Monitorar crashes
docker logs gtvision_mediamtx 2>&1 | findstr /C:"panic"

# Auto-restart no docker-compose.yml
restart: unless-stopped
```

### Prevenção
1. Adicionar healthcheck robusto no docker-compose.yml
2. Implementar auto-restart de câmeras problemáticas
3. Validar stream RTSP antes de provisionar
4. Usar TCP para câmeras instáveis

### Issue Upstream
- Reportado em: https://github.com/bluenviron/mediamtx/issues
- Versão afetada: gortsplib v5.3.0
- Aguardando fix na próxima versão

### Lição Aprendida
- Sempre usar `restart: unless-stopped` no docker-compose
- Implementar healthcheck que detecta crashes
- Validar qualidade do stream RTSP antes de adicionar câmera
- Manter lista de câmeras problemáticas conhecidas
