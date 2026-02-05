# ✅ CHECKLIST DE TESTES E VALIDAÇÃO

## TESTES DE GRAVAÇÃO

### Gravação Contínua
- [ ] Arquivo criado a cada hora exata (00.mp4, 01.mp4, ...)
- [ ] Estrutura de pastas: `/recordings/cam_X/YYYY-MM-DD/HH.mp4`
- [ ] Duração de cada arquivo: ~3600 segundos
- [ ] Formato: fMP4 (verificar com `ffprobe`)
- [ ] Codec: H.264 (sem reencoding)
- [ ] Sem gaps entre arquivos consecutivos
- [ ] Gravação funciona 24h sem interrupção

### Validação de Arquivos
```bash
# Verificar formato
ffprobe -v error -show_format /recordings/cam_1/2026-02-05/15.mp4

# Verificar codec
ffprobe -v error -select_streams v:0 -show_entries stream=codec_name /recordings/cam_1/2026-02-05/15.mp4

# Verificar duração
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 /recordings/cam_1/2026-02-05/15.mp4
```

- [ ] Formato: `mov,mp4,m4a,3gp,3g2,mj2`
- [ ] Codec: `h264`
- [ ] Duração: `3600.000000` (±10s)

### Retenção Cíclica
- [ ] Arquivos com mais de 168h são apagados automaticamente
- [ ] Deleção ocorre sem intervenção manual
- [ ] Gravação continua durante deleção
- [ ] Espaço em disco estabiliza em ~7 dias
- [ ] Logs confirmam deleção: `docker logs gtvision_mediamtx | grep delete`

### Testes de Falha

#### Restart do MediaMTX
```bash
# Durante gravação (ex: 15:30)
docker restart gtvision_mediamtx
```
- [ ] Arquivo 15.mp4 existe (pode estar incompleto)
- [ ] Gravação retoma automaticamente em < 30s
- [ ] Arquivo 16.mp4 é criado normalmente

#### Câmera Offline
```bash
# Desconectar câmera por 10 minutos
# Reconectar
```
- [ ] MediaMTX detecta desconexão
- [ ] Arquivo tem gap de 10 minutos (esperado)
- [ ] MediaMTX reconecta automaticamente
- [ ] Gravação continua após reconexão

#### Disco Cheio
```bash
# Simular disco cheio
dd if=/dev/zero of=/recordings/dummy.bin bs=1G count=100
```
- [ ] MediaMTX apaga arquivos antigos primeiro
- [ ] Gravação continua (não para)
- [ ] Alerta de disco cheio é disparado
- [ ] Sistema se recupera automaticamente

---

## TESTES DE PLAYBACK

### API de Timeline
```bash
curl http://localhost:8006/cameras/1/timeline?date=2026-02-05
```
- [ ] Retorna lista de segmentos
- [ ] Cada segmento tem: start, end, file_path, size_bytes
- [ ] Máximo 24 segmentos por dia
- [ ] Segmentos ordenados cronologicamente

### Iniciar Playback
```bash
curl -X POST http://localhost:8006/playback/start \
  -H "Content-Type: application/json" \
  -d '{"camera_id": 1, "start_time": "2026-02-05T15:30:00"}'
```
- [ ] Retorna `success: true`
- [ ] Retorna `hls_url` válida
- [ ] Playback inicia em < 2s
- [ ] HLS é servido corretamente

### Player Web
```javascript
// Testar no navegador
const hls = new Hls();
hls.loadSource('/hls/playback_cam_1_1738771800/index.m3u8');
hls.attachMedia(videoElement);
```
- [ ] Vídeo carrega em < 2s
- [ ] Seek funciona corretamente
- [ ] Player não percebe diferença (live vs gravação)
- [ ] Controles de playback funcionam (play, pause, seek)

### Múltiplos Playbacks
```bash
# 5 playbacks simultâneos
for i in {1..5}; do
  curl -X POST http://localhost:8006/playback/start \
    -d "{\"camera_id\": $i, \"start_time\": \"2026-02-05T15:00:00\"}" &
done
```
- [ ] Todos os playbacks iniciam corretamente
- [ ] CPU do MediaMTX < 80%
- [ ] Latência de cada playback < 2s
- [ ] Sem erros de memória

---

## TESTES DE ESCALA

### 12 Câmeras por Nó
```bash
# Provisionar 12 câmeras
for i in {1..12}; do
  curl -X POST http://localhost:8001/cameras/provision \
    -d "{\"camera_id\": $i, \"rtsp_url\": \"rtsp://cam$i/stream\"}"
done
```
- [ ] Todas as 12 câmeras gravando
- [ ] CPU < 80%
- [ ] RAM < 1.5GB
- [ ] Disco I/O < 100 MB/s
- [ ] Sem perda de frames

### 120 Câmeras (10 Nós)
```bash
# Provisionar 120 câmeras em 10 nós
for i in {1..120}; do
  curl -X POST http://orchestrator:8007/cameras/$i/allocate
done
```
- [ ] Distribuição uniforme (12 câmeras/nó)
- [ ] Todos os nós com CPU < 70%
- [ ] Gravação contínua em todas as câmeras
- [ ] Playback funcional em todas as câmeras
- [ ] Sem falhas por 24h

### Failover de Nó
```bash
# Parar nó 2
docker stop mediamtx_node_2

# Aguardar 30s
sleep 30
```
- [ ] Health check detecta nó offline
- [ ] Câmeras são redistribuídas automaticamente
- [ ] Gravação continua sem perda
- [ ] Playback continua funcionando
- [ ] Nó é recriado automaticamente (ASG)

---

## TESTES DE PERFORMANCE

### Latência de Live Streaming
```bash
# Medir latência do HLS
time curl -s http://localhost:8888/cam_1/index.m3u8 > /dev/null
```
- [ ] Latência < 500ms
- [ ] Throughput > 50 Mbps (12 câmeras × 4 Mbps)

### Latência de Playback
```bash
# Medir tempo de início de playback
time curl -X POST http://localhost:8006/playback/start \
  -d '{"camera_id": 1, "start_time": "2026-02-05T15:00:00"}'
```
- [ ] Resposta da API < 200ms
- [ ] Primeiro frame do HLS < 2s

### I/O de Disco
```bash
# Teste de escrita
dd if=/dev/zero of=/recordings/test.bin bs=1M count=10000 oflag=direct

# Teste de leitura
dd if=/recordings/test.bin of=/dev/null bs=1M iflag=direct
```
- [ ] Escrita > 500 MB/s
- [ ] Leitura > 600 MB/s
- [ ] IOPS > 3000

### CPU e Memória
```bash
# Monitorar por 1 hora
docker stats gtvision_mediamtx --no-stream
```
- [ ] CPU médio < 60%
- [ ] CPU pico < 80%
- [ ] RAM médio < 1GB
- [ ] RAM pico < 1.5GB

---

## TESTES DE DEPLOY

### Deploy Local (Docker Compose)
```bash
docker-compose up -d
```
- [ ] Todos os serviços iniciam corretamente
- [ ] Health checks passam
- [ ] Câmeras podem ser provisionadas
- [ ] Gravação inicia automaticamente

### Deploy AWS (Terraform)
```bash
cd terraform/environments/production
terraform apply
```
- [ ] Infraestrutura criada sem erros
- [ ] 10 nós EC2 criados
- [ ] EBS volumes anexados
- [ ] Security groups configurados
- [ ] Load balancer funcional

### CI/CD Pipeline
```bash
# Push para main
git push origin main
```
- [ ] Testes automatizados passam
- [ ] Build de imagens Docker bem-sucedido
- [ ] Deploy para staging automático
- [ ] Smoke tests passam
- [ ] Deploy para produção (manual approval)

### Blue-Green Deploy
```bash
./scripts/blue_green_deploy.sh
```
- [ ] Nova versão deployada no target group inativo
- [ ] Health checks passam
- [ ] Traffic switch sem downtime
- [ ] Rollback funciona se houver erros

---

## TESTES DE SEGURANÇA

### Criptografia
- [ ] Gravações criptografadas (AES-256)
- [ ] HTTPS em todas as APIs
- [ ] Certificados SSL válidos
- [ ] TLS 1.2+ apenas

### Autenticação
- [ ] API requer autenticação
- [ ] Tokens JWT válidos
- [ ] Sessões expiram corretamente
- [ ] Rate limiting funciona

### Auditoria
- [ ] Acessos a playback são logados
- [ ] Logs incluem: user_id, timestamp, IP, ação
- [ ] Logs são enviados para CloudWatch
- [ ] Retenção de logs: 90 dias

### Penetration Testing
```bash
# OWASP ZAP
docker run -t owasp/zap2docker-stable zap-baseline.py -t https://api.gtvision.com

# Nmap
nmap -sV -sC api.gtvision.com
```
- [ ] Sem vulnerabilidades críticas
- [ ] Sem portas desnecessárias abertas
- [ ] SSL Labs: A+ rating

---

## TESTES DE BACKUP E DR

### Backup para S3
```bash
# Executar script de backup
/opt/scripts/sync_to_s3.sh
```
- [ ] Gravações de ontem são sincronizadas
- [ ] Arquivos no S3 estão completos
- [ ] Lifecycle policy funciona (7d → 30d → 1y)

### Restore do S3
```bash
# Restaurar dia específico
./scripts/restore_from_s3.sh 42 2026-02-05
```
- [ ] Arquivos são baixados corretamente
- [ ] Playback funciona após restore
- [ ] Tempo de restore < 10 minutos

### Disaster Recovery
```bash
# Simular perda de nó
aws ec2 terminate-instances --instance-ids i-xxx
```
- [ ] ASG cria nova instância automaticamente
- [ ] Nova instância se registra no orchestrator
- [ ] Câmeras são redistribuídas
- [ ] Gravações continuam sem perda

---

## TESTES DE MONITORAMENTO

### CloudWatch Metrics
- [ ] Métricas de disco são coletadas
- [ ] Métricas de CPU são coletadas
- [ ] Métricas customizadas funcionam
- [ ] Dashboards exibem dados corretos

### Alarmes
```bash
# Simular disco cheio
dd if=/dev/zero of=/recordings/dummy.bin bs=1G count=2900
```
- [ ] Alarme de disco cheio dispara
- [ ] Notificação SNS é enviada
- [ ] Email é recebido
- [ ] Alarme volta ao normal após limpeza

### Logs
- [ ] Logs do MediaMTX no CloudWatch
- [ ] Logs do backend no CloudWatch
- [ ] Logs de auditoria separados
- [ ] Busca de logs funciona

---

## CHECKLIST DE PRODUÇÃO

### Pré-Deploy
- [ ] Todos os testes passam
- [ ] Documentação atualizada
- [ ] Runbooks criados
- [ ] Equipe treinada
- [ ] Backup testado
- [ ] Rollback testado

### Deploy
- [ ] Deploy em horário de baixo tráfego
- [ ] Monitoramento ativo durante deploy
- [ ] Smoke tests após deploy
- [ ] Verificação de logs
- [ ] Confirmação de métricas

### Pós-Deploy
- [ ] Sistema estável por 24h
- [ ] Sem erros críticos
- [ ] Performance dentro do esperado
- [ ] Custos dentro do orçamento
- [ ] Clientes notificados

---

## MÉTRICAS DE SUCESSO

### Disponibilidade
- [ ] Uptime > 99.9% (< 43 minutos de downtime/mês)
- [ ] Zero perda de gravações
- [ ] Failover automático funciona

### Performance
- [ ] Latência de live < 2s
- [ ] Latência de playback < 2s
- [ ] CPU médio < 60%
- [ ] Disco I/O < 100 MB/s

### Escala
- [ ] 120 câmeras gravando 24/7
- [ ] 10 nós MediaMTX operacionais
- [ ] Distribuição uniforme de carga
- [ ] Capacidade de expansão para 200 câmeras

### Custos
- [ ] Custo total < $3,000/mês
- [ ] Custo por câmera < $25/mês
- [ ] Otimizações aplicadas (Reserved Instances)

### Operacional
- [ ] Deploy sem downtime
- [ ] Rollback em < 5 minutos
- [ ] Troubleshooting em < 15 minutos
- [ ] Equipe autônoma
