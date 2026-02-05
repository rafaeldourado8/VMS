# ⚠️ RISCOS E MITIGAÇÕES

## RISCOS TÉCNICOS

### 1. DISCO CHEIO

**Probabilidade**: Média  
**Impacto**: Alto  
**Severidade**: 🔴 Crítico

#### Cenário
- Gravação consome mais espaço que o esperado
- Retenção automática falha
- Disco enche antes de 7 dias
- Gravação para completamente

#### Sinais de Alerta
```bash
# Disco > 80%
df -h /recordings | awk '{print $5}' | grep -o '[0-9]*' | head -1
```

#### Mitigação Preventiva
1. **Monitoramento Proativo**
```yaml
# CloudWatch Alarm
DiskUsageAlarm:
  Threshold: 80%
  Period: 5 minutes
  Action: SNS notification
```

2. **Retenção Automática**
```yaml
# mediamtx.yml
recordDeleteAfter: 168h  # 7 dias
```

3. **Limpeza Forçada**
```bash
# Cron diário (02:00)
0 2 * * * find /recordings -type f -mtime +7 -delete
```

4. **Expansão Automática (AWS)**
```python
# Lambda function
def expand_ebs_if_needed(volume_id, current_size):
    usage = get_disk_usage(volume_id)
    if usage > 85:
        new_size = current_size + 500  # +500GB
        ec2.modify_volume(VolumeId=volume_id, Size=new_size)
```

#### Mitigação Reativa
```bash
# 1. Identificar arquivos grandes
du -sh /recordings/*/* | sort -rh | head -20

# 2. Deletar arquivos mais antigos manualmente
find /recordings -type f -mtime +5 -delete

# 3. Expandir disco (AWS)
aws ec2 modify-volume --volume-id vol-xxx --size 4000

# 4. Resize filesystem
resize2fs /dev/sdf
```

---

### 2. FALHA DE REDE (CÂMERA OFFLINE)

**Probabilidade**: Alta  
**Impacto**: Médio  
**Severidade**: 🟡 Médio

#### Cenário
- Câmera perde conexão de rede
- RTSP stream interrompido
- Buraco na gravação
- Cliente reclama de falta de vídeo

#### Sinais de Alerta
```bash
# Verificar status da câmera
curl http://mediamtx:9997/v3/paths/get/cam_42 | jq '.ready'
# false = offline
```

#### Mitigação Preventiva
1. **Reconexão Automática**
```yaml
# mediamtx.yml (já configurado)
pathDefaults:
  sourceOnDemand: no  # Mantém conexão sempre ativa
  rtspTransport: tcp  # TCP é mais confiável que UDP
```

2. **Health Check de Câmeras**
```python
# services/camera_monitor.py
async def check_camera_health():
    cameras = get_all_cameras()
    for cam in cameras:
        status = await get_camera_status(cam.id)
        if not status['ready']:
            # Alerta
            send_alert(f"Camera {cam.id} offline")
            # Tentar reconectar
            await reconnect_camera(cam.id)
```

3. **Redundância de Rede**
- Câmeras com 2 NICs (rede primária + backup)
- Switch com link aggregation
- Monitoramento de switch (SNMP)

#### Mitigação Reativa
```bash
# 1. Verificar conectividade
ping 192.168.1.100

# 2. Testar RTSP manualmente
ffprobe rtsp://192.168.1.100:554/stream1

# 3. Reprovisionar câmera
curl -X POST http://streaming:8001/cameras/provision \
  -d '{"camera_id": 42, "rtsp_url": "rtsp://..."}'

# 4. Reiniciar câmera (ONVIF)
curl -X POST http://onvif:8005/cameras/42/reboot
```

---

### 3. RESTART DO MEDIAMTX

**Probabilidade**: Média  
**Impacto**: Médio  
**Severidade**: 🟡 Médio

#### Cenário
- MediaMTX crashea ou é reiniciado
- Arquivo atual fica incompleto
- Gravação para por alguns segundos
- Possível corrupção de arquivo

#### Sinais de Alerta
```bash
# Verificar uptime do container
docker inspect gtvision_mediamtx | jq '.[0].State.StartedAt'

# Logs de crash
docker logs gtvision_mediamtx | grep -i "panic\|fatal\|error"
```

#### Mitigação Preventiva
1. **Limites de Recursos**
```yaml
# docker-compose.yml
mediamtx:
  deploy:
    resources:
      limits:
        cpus: '2.5'
        memory: 2G
      reservations:
        cpus: '1.0'
        memory: 512M
```

2. **Health Check**
```yaml
healthcheck:
  test: ["CMD", "wget", "-q", "--spider", "http://localhost:9997/v3/config/global/get"]
  interval: 10s
  timeout: 5s
  retries: 3
  start_period: 10s
```

3. **Restart Policy**
```yaml
restart: unless-stopped
```

4. **Validação de Arquivos**
```bash
# Cron a cada hora
0 * * * * /opt/scripts/validate_recordings.sh
```

```bash
#!/bin/bash
# validate_recordings.sh
CURRENT_HOUR=$(date +%H)
PREV_HOUR=$(date -d '1 hour ago' +%H)
DATE=$(date +%Y-%m-%d)

for cam in /recordings/cam_*; do
  cam_id=$(basename $cam)
  file="$cam/$DATE/$PREV_HOUR.mp4"
  
  if [ -f "$file" ]; then
    # Validar com ffprobe
    if ! ffprobe -v error "$file" 2>&1 | grep -q "Duration"; then
      echo "⚠️ Arquivo corrompido: $file"
      # Marcar para reprocessamento
      touch "$file.corrupted"
    fi
  fi
done
```

#### Mitigação Reativa
```bash
# 1. Verificar arquivo incompleto
ffprobe /recordings/cam_42/2026-02-05/15.mp4

# 2. Se corrompido, tentar recuperar
ffmpeg -i /recordings/cam_42/2026-02-05/15.mp4 -c copy /recordings/cam_42/2026-02-05/15_fixed.mp4

# 3. Se irrecuperável, marcar como perdido
mv /recordings/cam_42/2026-02-05/15.mp4 /recordings/lost/

# 4. Investigar causa do crash
docker logs gtvision_mediamtx --tail 1000 > crash.log
```

---

### 4. CORRUPÇÃO DE ARQUIVO

**Probabilidade**: Baixa  
**Impacto**: Médio  
**Severidade**: 🟢 Baixo

#### Cenário
- Arquivo MP4 corrompido (header inválido)
- Playback falha
- Cliente não consegue assistir gravação

#### Sinais de Alerta
```bash
# Validar arquivo
ffprobe -v error /recordings/cam_42/2026-02-05/15.mp4
# Erro: "moov atom not found"
```

#### Mitigação Preventiva
1. **Formato fMP4** (já configurado)
```yaml
recordFormat: fmp4  # Headers distribuídos, mais recuperável
```

2. **Validação Periódica**
```python
# services/file_validator.py
import subprocess
from pathlib import Path

def validate_recording(file_path):
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'error', file_path],
            capture_output=True,
            timeout=10
        )
        return result.returncode == 0
    except:
        return False

# Validar arquivos de ontem
yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
for file in Path(f'/recordings').rglob(f'*/{yesterday}/*.mp4'):
    if not validate_recording(file):
        alert(f"Corrupted file: {file}")
```

3. **Backup Imediato**
```bash
# Sincronizar para S3 após 1 hora
# (arquivo já está fechado e completo)
```

#### Mitigação Reativa
```bash
# 1. Tentar recuperar com ffmpeg
ffmpeg -i corrupted.mp4 -c copy fixed.mp4

# 2. Usar ferramenta especializada
untrunc reference.mp4 corrupted.mp4

# 3. Se irrecuperável, restaurar do S3
aws s3 cp s3://gtvision-recordings/cam_42/2026-02-05/15.mp4 /recordings/cam_42/2026-02-05/

# 4. Notificar cliente
# "Gravação de 15:00-16:00 está indisponível"
```

---

### 5. ESCALA (120 CÂMERAS)

**Probabilidade**: Média  
**Impacto**: Alto  
**Severidade**: 🔴 Crítico

#### Cenário
- Um único MediaMTX não aguenta 120 câmeras
- CPU > 100%
- Frames dropados
- Gravações com falhas

#### Sinais de Alerta
```bash
# CPU > 80%
docker stats gtvision_mediamtx --no-stream | awk '{print $3}'

# Frames dropados
docker logs gtvision_mediamtx | grep "dropped"
```

#### Mitigação Preventiva
1. **Arquitetura Multi-Nó** (obrigatório)
```
10 nós × 12 câmeras = 120 câmeras
```

2. **Balanceamento de Carga**
```python
def allocate_camera_smart(camera_id):
    # Seleciona nó com menor carga
    node = MediaNode.objects.filter(
        status='active',
        current_cameras__lt=12
    ).order_by('current_cameras').first()
    
    return node
```

3. **Auto-Scaling (AWS)**
```hcl
resource "aws_autoscaling_policy" "scale_up" {
  name                   = "mediamtx-scale-up"
  scaling_adjustment     = 2
  adjustment_type        = "ChangeInCapacity"
  cooldown               = 300
  autoscaling_group_name = aws_autoscaling_group.mediamtx.name
}

resource "aws_cloudwatch_metric_alarm" "cpu_high" {
  alarm_name          = "mediamtx-cpu-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  threshold           = 70
  alarm_actions       = [aws_autoscaling_policy.scale_up.arn]
}
```

4. **Limites por Nó**
```python
MAX_CAMERAS_PER_NODE = 12

if node.current_cameras >= MAX_CAMERAS_PER_NODE:
    raise Exception("Node full, allocate to another node")
```

#### Mitigação Reativa
```bash
# 1. Identificar nó sobrecarregado
curl http://orchestrator:8007/nodes/status

# 2. Migrar câmeras para outro nó
curl -X POST http://orchestrator:8007/cameras/42/migrate \
  -d '{"target_node_id": 5}'

# 3. Adicionar novo nó (AWS)
terraform apply -var="node_count=11"

# 4. Redistribuir carga
curl -X POST http://orchestrator:8007/rebalance
```

---

## RISCOS OPERACIONAIS

### 6. CUSTO AWS ALTO

**Probabilidade**: Média  
**Impacto**: Alto  
**Severidade**: 🟡 Médio

#### Cenário
- Custo mensal > $5,000
- Orçamento estourado
- Necessidade de otimização urgente

#### Sinais de Alerta
```bash
# Verificar custo atual
aws ce get-cost-and-usage \
  --time-period Start=2026-02-01,End=2026-02-28 \
  --granularity MONTHLY \
  --metrics BlendedCost
```

#### Mitigação Preventiva
1. **Reserved Instances** (-40%)
```bash
# Comprar RIs de 1 ano
aws ec2 purchase-reserved-instances-offering \
  --reserved-instances-offering-id xxx \
  --instance-count 10
```

2. **Savings Plans** (-30%)
```bash
# Commit de $2,000/mês por 1 ano
```

3. **EBS gp3 vs gp2** (-20%)
```hcl
volume_type = "gp3"  # Mais barato que gp2
```

4. **S3 Intelligent-Tiering** (-30%)
```hcl
storage_class = "INTELLIGENT_TIERING"
```

5. **Budget Alerts**
```hcl
resource "aws_budgets_budget" "monthly" {
  name              = "gtvision-monthly-budget"
  budget_type       = "COST"
  limit_amount      = "3000"
  limit_unit        = "USD"
  time_period_start = "2026-02-01_00:00"
  time_unit         = "MONTHLY"
  
  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 80
    threshold_type             = "PERCENTAGE"
    notification_type          = "ACTUAL"
    subscriber_email_addresses = ["ops@gtvision.com"]
  }
}
```

#### Mitigação Reativa
```bash
# 1. Identificar recursos caros
aws ce get-cost-and-usage \
  --time-period Start=2026-02-01,End=2026-02-28 \
  --granularity DAILY \
  --group-by Type=SERVICE

# 2. Reduzir retenção (7d → 5d)
recordDeleteAfter: 120h

# 3. Usar Spot Instances (não recomendado para produção)

# 4. Comprimir gravações antigas
gzip /recordings/cam_*/$(date -d '3 days ago' +%Y-%m-%d)/*.mp4
```

---

### 7. BUGS EM PRODUÇÃO

**Probabilidade**: Média  
**Impacto**: Alto  
**Severidade**: 🔴 Crítico

#### Cenário
- Deploy introduz bug crítico
- Sistema fica instável
- Clientes afetados
- Necessidade de rollback urgente

#### Sinais de Alerta
```bash
# Erros 5xx aumentam
aws cloudwatch get-metric-statistics \
  --namespace AWS/ApplicationELB \
  --metric-name HTTPCode_Target_5XX_Count \
  --start-time $(date -u -d '10 minutes ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 60 \
  --statistics Sum
```

#### Mitigação Preventiva
1. **CI/CD com Testes**
```yaml
# .github/workflows/ci.yml
- name: Run tests
  run: pytest --cov=. --cov-fail-under=80
```

2. **Deploy Blue-Green**
```bash
# Deploy gradual, rollback automático se erros
./scripts/blue_green_deploy.sh
```

3. **Canary Deployment**
```hcl
# 10% do tráfego para nova versão
# Se OK, 100%
# Se erros, rollback
```

4. **Feature Flags**
```python
if feature_enabled('new_playback_api'):
    return new_playback()
else:
    return old_playback()
```

#### Mitigação Reativa
```bash
# 1. Rollback imediato (< 5 minutos)
./scripts/rollback.sh

# 2. Verificar logs
aws logs tail /aws/ecs/gtvision-backend --follow

# 3. Hotfix
git revert HEAD
git push origin main

# 4. Post-mortem
# Documentar causa raiz e prevenção
```

---

## RISCOS DE SEGURANÇA

### 8. ACESSO NÃO AUTORIZADO

**Probabilidade**: Baixa  
**Impacto**: Alto  
**Severidade**: 🔴 Crítico

#### Cenário
- Invasor acessa gravações
- Dados sensíveis vazados
- Violação de LGPD
- Multa e perda de reputação

#### Mitigação Preventiva
1. **Criptografia**
```yaml
recordEncryption: aes-256-cbc
```

2. **Autenticação Forte**
```python
# JWT com expiração curta (1h)
# MFA obrigatório para admins
```

3. **Auditoria**
```python
# Log todos os acessos a playback
audit_log.info({
    'user_id': user.id,
    'action': 'playback_access',
    'camera_id': camera_id,
    'timestamp': datetime.utcnow()
})
```

4. **Penetration Testing**
```bash
# Trimestral
docker run -t owasp/zap2docker-stable zap-baseline.py -t https://api.gtvision.com
```

---

## MATRIZ DE RISCOS

| Risco | Probabilidade | Impacto | Severidade | Prioridade |
|-------|---------------|---------|------------|------------|
| Disco cheio | Média | Alto | 🔴 Crítico | 1 |
| Escala (120 cams) | Média | Alto | 🔴 Crítico | 2 |
| Bugs em produção | Média | Alto | 🔴 Crítico | 3 |
| Acesso não autorizado | Baixa | Alto | 🔴 Crítico | 4 |
| Custo AWS alto | Média | Alto | 🟡 Médio | 5 |
| Falha de rede | Alta | Médio | 🟡 Médio | 6 |
| Restart MediaMTX | Média | Médio | 🟡 Médio | 7 |
| Corrupção de arquivo | Baixa | Médio | 🟢 Baixo | 8 |

---

## PLANO DE CONTINGÊNCIA

### Cenário Catastrófico: Perda Total de Dados

**Probabilidade**: Muito Baixa  
**Impacto**: Catastrófico

#### Backup 3-2-1
- **3** cópias dos dados
- **2** tipos de mídia diferentes
- **1** cópia offsite

```
Cópia 1: EBS local (produção)
Cópia 2: S3 Standard (7-30 dias)
Cópia 3: S3 Glacier (1 ano)
```

#### Recovery Time Objective (RTO)
- **Crítico**: < 1 hora
- **Alto**: < 4 horas
- **Médio**: < 24 horas

#### Recovery Point Objective (RPO)
- **Gravações**: 0 (tempo real)
- **Backup S3**: 24 horas

#### Procedimento de DR
```bash
# 1. Criar nova infraestrutura
cd terraform/environments/dr
terraform apply

# 2. Restaurar dados do S3
aws s3 sync s3://gtvision-recordings-backup/ /recordings/

# 3. Atualizar DNS
aws route53 change-resource-record-sets \
  --hosted-zone-id Z123 \
  --change-batch file://dns-failover.json

# 4. Validar
curl https://api.gtvision.com/health
```

**Tempo total de recuperação**: < 2 horas
