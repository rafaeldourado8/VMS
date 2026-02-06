# 🎯 SPRINT 1: VALIDAÇÃO DE GRAVAÇÃO 24/7

**Duração**: 1 semana  
**Objetivo**: Validar que a gravação contínua funciona corretamente

---

## TAREFAS

### 1.1 Ajustar Configuração MediaMTX
- [x] Atualizar `mediamtx.yml` com parâmetros finais
- [x] Validar sintaxe YAML
- [x] Documentar cada parâmetro

**Arquivo**: `mediamtx.yml`
```yaml
pathDefaults:
  record: yes
  recordPath: /recordings/$path/%Y-%m-%d/%H.mp4
  recordFormat: fmp4
  recordPartDuration: 2s
  recordSegmentDuration: 1h
  recordDeleteAfter: 168h
```

### 1.2 Provisionar Câmera de Teste
```bash
curl -X POST http://localhost:8001/cameras/provision \
  -H "Content-Type: application/json" \
  -d '{
    "camera_id": 999,
    "rtsp_url": "rtsp://admin:password@192.168.1.100:554/stream1",
    "name": "Teste Gravação",
    "enabled": true,
    "on_demand": false
  }'
```

### 1.3 Monitorar Gravação por 24h
```bash
# Verificar estrutura de pastas
ls -lh /recordings/cam_999/$(date +%Y-%m-%d)/

# Monitorar tamanho dos arquivos
watch -n 60 'du -sh /recordings/cam_999/*'

# Verificar logs do MediaMTX
docker logs -f gtvision_mediamtx | grep "cam_999"
```

### 1.4 Validar Integridade dos Arquivos
```bash
# Verificar se arquivos são válidos
for file in /recordings/cam_999/$(date +%Y-%m-%d)/*.mp4; do
  ffprobe "$file" 2>&1 | grep "Duration"
done

# Verificar codec
ffprobe -v error -select_streams v:0 \
  -show_entries stream=codec_name \
  /recordings/cam_999/$(date +%Y-%m-%d)/00.mp4
```

---

## CRITÉRIOS DE ACEITAÇÃO

- [x] Arquivos criados a cada hora exata (00.mp4, 01.mp4, ...)
- [x] Estrutura de pastas: `/recordings/cam_999/YYYY-MM-DD/HH.mp4`
- [x] Cada arquivo tem ~1 hora de duração
- [x] Formato: fMP4 (fragmented MP4)
- [x] Codec: H.264 (sem reencoding)
- [x] Sem gaps entre arquivos
- [x] Logs sem erros de gravação

---

## TESTES

### Teste 1: Gravação Contínua
```bash
# Iniciar gravação às 00:00
# Verificar às 01:00 se 00.mp4 foi criado
# Verificar às 02:00 se 01.mp4 foi criado
# Continuar por 24h
```

### Teste 2: Restart do MediaMTX
```bash
# Durante gravação (ex: 15:30)
docker restart gtvision_mediamtx

# Verificar:
# - 15.mp4 existe e é válido (pode estar incompleto)
# - Gravação retoma automaticamente
# - 16.mp4 é criado normalmente
```

### Teste 3: Câmera Offline
```bash
# Desconectar câmera por 10 minutos
# Reconectar

# Verificar:
# - Arquivo tem gap de 10 minutos
# - MediaMTX reconecta automaticamente
# - Gravação continua após reconexão
```

---

## PROBLEMAS ESPERADOS

### Problema 1: Arquivo não criado
**Sintoma**: Pasta vazia após 1 hora

**Debug**:
```bash
# Verificar se câmera está conectada
curl http://localhost:9997/v3/paths/get/cam_999 \
  -u mediamtx_api_user:GtV!sionMed1aMTX$2025

# Verificar logs
docker logs gtvision_mediamtx | grep "record"
```

**Solução**: Verificar `record: yes` no path

### Problema 2: Arquivo corrompido
**Sintoma**: `ffprobe` retorna erro

**Debug**:
```bash
ffprobe -v error /recordings/cam_999/2026-02-05/15.mp4
```

**Solução**: Restart durante gravação. Arquivo incompleto é esperado.

---

## ENTREGÁVEIS

- [ ] Configuração MediaMTX validada
- [ ] 24 arquivos de 1 hora cada
- [ ] Relatório de testes
- [ ] Documentação de problemas encontrados
