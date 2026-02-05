# 🚀 QUICK START - COMECE AGORA

## ⏱️ 5 MINUTOS PARA COMEÇAR

### 1. Verificar Configuração Atual

```bash
# Verificar se MediaMTX está rodando
docker ps | grep mediamtx

# Verificar configuração de gravação
grep -A 6 "record:" mediamtx.yml
```

**Resultado esperado**:
```yaml
record: yes
recordPath: /recordings/%path/%Y-%m-%d/%H.mp4
recordFormat: fmp4
recordPartDuration: 2s
recordSegmentDuration: 1h
recordDeleteAfter: 168h
```

✅ **Se estiver correto, prossiga para o passo 2**  
❌ **Se estiver diferente, a configuração já foi ajustada no arquivo `mediamtx.yml`**

---

### 2. Reiniciar MediaMTX (Aplicar Nova Configuração)

```bash
# Reiniciar container
docker-compose restart mediamtx

# Aguardar 10 segundos
sleep 10

# Verificar se subiu corretamente
curl -s http://localhost:9997/v3/config/global/get | jq '.logLevel'
```

**Resultado esperado**: `"info"`

---

### 3. Provisionar Câmera de Teste

```bash
# Substitua pelos dados da sua câmera real
curl -X POST http://localhost:8001/cameras/provision \
  -H "Content-Type: application/json" \
  -d '{
    "camera_id": 999,
    "rtsp_url": "rtsp://admin:senha@192.168.1.100:554/stream1",
    "name": "Câmera Teste Gravação",
    "enabled": true,
    "on_demand": false
  }'
```

**Resultado esperado**:
```json
{
  "success": true,
  "camera_id": 999,
  "stream_path": "cam_999",
  "hls_url": "/hls/cam_999/index.m3u8",
  "message": "Provisionamento OK"
}
```

---

### 4. Verificar se Gravação Iniciou

```bash
# Aguardar 1 minuto
sleep 60

# Verificar se pasta foi criada
ls -la /recordings/cam_999/

# Verificar se arquivo está sendo gravado
ls -lh /recordings/cam_999/$(date +%Y-%m-%d)/
```

**Resultado esperado**:
```
-rw-r--r-- 1 root root 45M Feb  5 15:30 15.mp4
```

✅ **Se o arquivo existe e está crescendo, SUCESSO!**

---

### 5. Monitorar Gravação em Tempo Real

```bash
# Monitorar tamanho do arquivo atual (atualiza a cada 10s)
watch -n 10 'ls -lh /recordings/cam_999/$(date +%Y-%m-%d)/$(date +%H).mp4'
```

**Resultado esperado**: Tamanho aumentando a cada 10 segundos

---

## 📊 VALIDAÇÃO COMPLETA (15 MINUTOS)

### Validar Formato do Arquivo

```bash
# Instalar ffprobe (se necessário)
# docker exec -it gtvision_mediamtx apk add ffmpeg

# Validar arquivo
docker exec gtvision_mediamtx ffprobe -v error -show_format /recordings/cam_999/$(date +%Y-%m-%d)/$(date +%H).mp4
```

**Verificar**:
- ✅ `format_name=mov,mp4,m4a,3gp,3g2,mj2`
- ✅ `duration` está aumentando

### Validar Codec (Sem Reencoding)

```bash
docker exec gtvision_mediamtx ffprobe -v error -select_streams v:0 -show_entries stream=codec_name /recordings/cam_999/$(date +%Y-%m-%d)/$(date +%H).mp4
```

**Resultado esperado**: `codec_name=h264`

### Verificar Logs

```bash
# Logs do MediaMTX
docker logs gtvision_mediamtx | grep cam_999 | tail -20
```

**Buscar por**:
- ✅ `[RTSP] [conn] opened`
- ✅ `[path cam_999] ready`
- ❌ Não deve ter: `error`, `failed`, `dropped`

---

## 🎯 PRÓXIMOS PASSOS

### Hoje (Dia 1)
- [x] Configuração ajustada
- [x] MediaMTX reiniciado
- [x] Câmera provisionada
- [x] Gravação iniciada
- [ ] **Deixar gravando por 24h**

### Amanhã (Dia 2)
```bash
# Verificar se 24 arquivos foram criados
ls -lh /recordings/cam_999/$(date -d 'yesterday' +%Y-%m-%d)/ | wc -l
# Resultado esperado: 24
```

### Semana 1 (Sprint 1)
- [ ] Gravação contínua por 7 dias
- [ ] Validar retenção cíclica
- [ ] Testes de falha (restart, câmera offline)
- [ ] Documentar resultados

**Consulte**: `docs/mvp/sprints/SPRINT_01.md`

---

## 🆘 TROUBLESHOOTING RÁPIDO

### Problema: Pasta /recordings vazia

**Causa**: Gravação não iniciou

**Solução**:
```bash
# 1. Verificar se câmera está conectada
curl http://localhost:9997/v3/paths/get/cam_999 | jq '.ready'

# 2. Se false, verificar RTSP
docker exec gtvision_mediamtx ffprobe rtsp://admin:senha@192.168.1.100:554/stream1

# 3. Verificar logs
docker logs gtvision_mediamtx | grep cam_999 | grep error
```

### Problema: Arquivo não cresce

**Causa**: Stream não está chegando

**Solução**:
```bash
# Verificar se há bytes recebidos
curl http://localhost:9997/v3/paths/get/cam_999 | jq '.bytesReceived'

# Se 0, problema na câmera
# Se > 0, problema na gravação
```

### Problema: MediaMTX não inicia

**Causa**: Erro na configuração YAML

**Solução**:
```bash
# Validar YAML
docker run --rm -v $(pwd)/mediamtx.yml:/mediamtx.yml bluenviron/mediamtx:latest-ffmpeg

# Ver erro específico
docker logs gtvision_mediamtx
```

---

## 📞 PRECISA DE AJUDA?

### Documentação Completa
```bash
# Ler índice
cat docs/mvp/INDEX.md

# Ler README principal
cat docs/mvp/README.md

# Ver checklist de testes
cat docs/mvp/CHECKLIST_TESTES.md
```

### Comandos Úteis

```bash
# Status geral
docker-compose ps

# Logs de todos os serviços
docker-compose logs -f

# Reiniciar tudo
docker-compose restart

# Parar tudo
docker-compose down

# Subir tudo novamente
docker-compose up -d
```

---

## ✅ CHECKLIST DE SUCESSO

Marque conforme avança:

- [ ] MediaMTX rodando
- [ ] Configuração de gravação correta
- [ ] Câmera provisionada
- [ ] Pasta `/recordings/cam_999/` criada
- [ ] Arquivo `.mp4` sendo gravado
- [ ] Tamanho do arquivo aumentando
- [ ] Formato fMP4 validado
- [ ] Codec H.264 (sem reencoding)
- [ ] Logs sem erros
- [ ] Gravação rodando por 24h

**Quando todos estiverem marcados, você completou a Sprint 1! 🎉**

---

## 🎓 APRENDIZADO

### O que você acabou de fazer:

1. ✅ Configurou gravação 24/7 no MediaMTX
2. ✅ Provisionou uma câmera dinamicamente
3. ✅ Iniciou gravação contínua em fMP4
4. ✅ Validou formato e codec
5. ✅ Monitorou gravação em tempo real

### Próximos conceitos:

- **Retenção cíclica**: Arquivos antigos são apagados automaticamente
- **Playback**: Assistir gravações antigas via HLS
- **Escala**: Múltiplos nós MediaMTX para 120 câmeras
- **Deploy AWS**: Infraestrutura em nuvem

---

## 📚 LEITURA RECOMENDADA

1. **[README.md](docs/mvp/README.md)** - Entenda o projeto completo
2. **[ARQUITETURA_TECNICA.md](docs/mvp/ARQUITETURA_TECNICA.md)** - Como funciona por baixo dos panos
3. **[sprints/SPRINT_01.md](docs/mvp/sprints/SPRINT_01.md)** - Detalhes da Sprint 1

---

**Boa sorte! 🚀**

Se tudo funcionou, você está pronto para a Sprint 1.  
Se teve problemas, consulte a seção de Troubleshooting ou a documentação completa.
