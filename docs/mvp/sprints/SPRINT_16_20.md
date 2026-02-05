# 🎯 SPRINTS 16-20: CI/CD E PRODUÇÃO

## SPRINT 16: PIPELINE CI/CD

### Objetivo
Automatizar testes, build e deploy via GitHub Actions

### .github/workflows/ci.yml

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  AWS_REGION: us-east-1
  ECR_REGISTRY: 123456789012.dkr.ecr.us-east-1.amazonaws.com

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r backend/requirements.txt
          pip install pytest pytest-cov
      
      - name: Run tests
        run: |
          cd backend
          pytest --cov=. --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}
      
      - name: Login to ECR
        run: |
          aws ecr get-login-password --region $AWS_REGION | \
          docker login --username AWS --password-stdin $ECR_REGISTRY
      
      - name: Build and push images
        run: |
          # Backend
          docker build -t $ECR_REGISTRY/gtvision-backend:${{ github.sha }} ./backend
          docker push $ECR_REGISTRY/gtvision-backend:${{ github.sha }}
          
          # Streaming
          docker build -t $ECR_REGISTRY/gtvision-streaming:${{ github.sha }} ./services/streaming
          docker push $ECR_REGISTRY/gtvision-streaming:${{ github.sha }}
          
          # Playback
          docker build -t $ECR_REGISTRY/gtvision-playback:${{ github.sha }} ./services/playback
          docker push $ECR_REGISTRY/gtvision-playback:${{ github.sha }}
      
      - name: Tag as latest
        run: |
          docker tag $ECR_REGISTRY/gtvision-backend:${{ github.sha }} $ECR_REGISTRY/gtvision-backend:latest
          docker push $ECR_REGISTRY/gtvision-backend:latest

  deploy-staging:
    needs: build
    runs-on: ubuntu-latest
    environment: staging
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}
      
      - name: Deploy to ECS (Staging)
        run: |
          aws ecs update-service \
            --cluster gtvision-staging \
            --service backend \
            --force-new-deployment
      
      - name: Wait for deployment
        run: |
          aws ecs wait services-stable \
            --cluster gtvision-staging \
            --services backend
      
      - name: Run smoke tests
        run: |
          curl -f https://staging.gtvision.com/health || exit 1

  deploy-production:
    needs: deploy-staging
    runs-on: ubuntu-latest
    environment: production
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}
      
      - name: Deploy to ECS (Production)
        run: |
          aws ecs update-service \
            --cluster gtvision-production \
            --service backend \
            --force-new-deployment \
            --desired-count 3
      
      - name: Wait for deployment
        run: |
          aws ecs wait services-stable \
            --cluster gtvision-production \
            --services backend
      
      - name: Run smoke tests
        run: |
          curl -f https://api.gtvision.com/health || exit 1
      
      - name: Notify Slack
        uses: slackapi/slack-github-action@v1
        with:
          payload: |
            {
              "text": "✅ Deploy to production successful: ${{ github.sha }}"
            }
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```

### Testes Automatizados

```python
# backend/tests/test_recording.py
import pytest
from datetime import datetime, timedelta

def test_timeline_api(client):
    """Testa API de timeline."""
    response = client.get('/api/playback/cameras/1/timeline?date=2026-02-05')
    assert response.status_code == 200
    data = response.json()
    assert 'segments' in data
    assert len(data['segments']) <= 24

def test_playback_start(client):
    """Testa início de playback."""
    response = client.post('/api/playback/start', json={
        'camera_id': 1,
        'start_time': '2026-02-05T15:00:00'
    })
    assert response.status_code == 200
    data = response.json()
    assert data['success'] is True
    assert 'hls_url' in data

def test_recording_retention(client):
    """Testa retenção de 7 dias."""
    # Simula arquivo de 8 dias atrás
    old_date = (datetime.now() - timedelta(days=8)).strftime('%Y-%m-%d')
    response = client.get(f'/api/playback/cameras/1/timeline?date={old_date}')
    data = response.json()
    assert len(data['segments']) == 0  # Deve estar vazio
```

---

## SPRINT 17: DEPLOY BLUE-GREEN

### Objetivo
Deploy sem downtime com rollback automático

### Estratégia Blue-Green

```
┌─────────────┐
│   Route53   │
└──────┬──────┘
       │
       ├─────────────┐
       │             │
   ┌───▼───┐    ┌───▼───┐
   │ Blue  │    │ Green │
   │ (old) │    │ (new) │
   └───────┘    └───────┘
```

### Terraform (Blue-Green)

```hcl
# terraform/blue_green.tf

resource "aws_lb_target_group" "blue" {
  name     = "gtvision-backend-blue"
  port     = 8000
  protocol = "HTTP"
  vpc_id   = module.vpc.vpc_id
}

resource "aws_lb_target_group" "green" {
  name     = "gtvision-backend-green"
  port     = 8000
  protocol = "HTTP"
  vpc_id   = module.vpc.vpc_id
}

resource "aws_lb_listener_rule" "production" {
  listener_arn = aws_lb_listener.https.arn
  priority     = 100
  
  action {
    type             = "forward"
    target_group_arn = var.active_target_group == "blue" ? 
                       aws_lb_target_group.blue.arn : 
                       aws_lb_target_group.green.arn
  }
  
  condition {
    path_pattern {
      values = ["/api/*"]
    }
  }
}
```

### Script de Deploy

```bash
#!/bin/bash
# scripts/blue_green_deploy.sh

set -e

CURRENT=$(aws elbv2 describe-target-groups \
  --names gtvision-backend-blue gtvision-backend-green \
  --query 'TargetGroups[?TargetHealth.State==`healthy`].TargetGroupName' \
  --output text)

if [ "$CURRENT" == "blue" ]; then
  NEW="green"
else
  NEW="blue"
fi

echo "Current: $CURRENT"
echo "Deploying to: $NEW"

# 1. Deploy nova versão no target group inativo
aws ecs update-service \
  --cluster gtvision-production \
  --service backend-$NEW \
  --force-new-deployment

# 2. Aguardar health check
echo "Waiting for health checks..."
sleep 60

# 3. Verificar saúde
HEALTHY=$(aws elbv2 describe-target-health \
  --target-group-arn $(aws elbv2 describe-target-groups \
    --names gtvision-backend-$NEW \
    --query 'TargetGroups[0].TargetGroupArn' \
    --output text) \
  --query 'TargetHealthDescriptions[?TargetHealth.State==`healthy`] | length(@)')

if [ "$HEALTHY" -lt 2 ]; then
  echo "❌ Health check failed. Aborting."
  exit 1
fi

# 4. Smoke tests
curl -f https://api.gtvision.com/health || exit 1

# 5. Switch traffic
aws elbv2 modify-listener \
  --listener-arn $LISTENER_ARN \
  --default-actions Type=forward,TargetGroupArn=$(aws elbv2 describe-target-groups \
    --names gtvision-backend-$NEW \
    --query 'TargetGroups[0].TargetGroupArn' \
    --output text)

echo "✅ Traffic switched to $NEW"

# 6. Monitorar por 5 minutos
echo "Monitoring for 5 minutes..."
sleep 300

# 7. Verificar erros
ERRORS=$(aws cloudwatch get-metric-statistics \
  --namespace AWS/ApplicationELB \
  --metric-name HTTPCode_Target_5XX_Count \
  --start-time $(date -u -d '5 minutes ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum \
  --query 'Datapoints[0].Sum' \
  --output text)

if [ "$ERRORS" != "None" ] && [ "$ERRORS" -gt 10 ]; then
  echo "❌ Too many errors. Rolling back..."
  # Rollback
  aws elbv2 modify-listener \
    --listener-arn $LISTENER_ARN \
    --default-actions Type=forward,TargetGroupArn=$(aws elbv2 describe-target-groups \
      --names gtvision-backend-$CURRENT \
      --query 'TargetGroups[0].TargetGroupArn' \
      --output text)
  exit 1
fi

echo "✅ Deploy successful!"
```

---

## SPRINT 18: OTIMIZAÇÕES DE PERFORMANCE

### Objetivo
Tuning fino para produção

### 1. Otimização MediaMTX

```yaml
# mediamtx.yml (otimizado)
pathDefaults:
  # Gravação
  record: yes
  recordPath: /recordings/%path/%Y-%m-%d/%H.mp4
  recordFormat: fmp4
  recordPartDuration: 2s
  recordSegmentDuration: 1h
  recordDeleteAfter: 168h
  
  # Performance
  readBufferCount: 2048        # Buffer maior para gravação
  rtspUDPReadBufferSize: 131072  # 128KB (dobro do padrão)
  
  # HLS otimizado
  hlsSegmentDuration: 4s
  hlsSegmentCount: 6
  hlsPartDuration: 1s
  hlsMuxerCloseAfter: 30s
```

### 2. Otimização de Disco (I/O)

```bash
# /etc/fstab
/dev/sdf /recordings ext4 noatime,nodiratime,data=writeback 0 2

# Remount
mount -o remount /recordings

# Verificar
mount | grep recordings
```

### 3. Compressão de Gravações Antigas

```python
# scripts/compress_old_recordings.py
import os
import subprocess
from datetime import datetime, timedelta

RECORDINGS_PATH = "/recordings"
COMPRESS_AFTER_DAYS = 3

def compress_old_files():
    cutoff = datetime.now() - timedelta(days=COMPRESS_AFTER_DAYS)
    
    for cam_dir in os.listdir(RECORDINGS_PATH):
        cam_path = os.path.join(RECORDINGS_PATH, cam_dir)
        
        for date_dir in os.listdir(cam_path):
            date_path = os.path.join(cam_path, date_dir)
            date_obj = datetime.strptime(date_dir, '%Y-%m-%d')
            
            if date_obj < cutoff:
                for file in os.listdir(date_path):
                    if file.endswith('.mp4') and not file.endswith('.mp4.gz'):
                        file_path = os.path.join(date_path, file)
                        
                        # Comprimir com gzip
                        subprocess.run(['gzip', '-9', file_path])
                        print(f"Compressed: {file_path}")

if __name__ == '__main__':
    compress_old_files()
```

### 4. Benchmarks

```bash
# Teste de escrita
dd if=/dev/zero of=/recordings/test.bin bs=1M count=10000 oflag=direct
# Resultado esperado: > 500 MB/s

# Teste de leitura
dd if=/recordings/test.bin of=/dev/null bs=1M iflag=direct
# Resultado esperado: > 600 MB/s

# IOPS
fio --name=random-write --ioengine=libaio --rw=randwrite --bs=4k --size=1G --numjobs=4 --runtime=60 --time_based --end_fsync=1 --filename=/recordings/fio-test
# Resultado esperado: > 3000 IOPS
```

---

## SPRINT 19: SEGURANÇA E COMPLIANCE

### Objetivo
Garantir segurança e conformidade LGPD

### 1. Criptografia de Gravações

```yaml
# mediamtx.yml
pathDefaults:
  record: yes
  recordPath: /recordings/%path/%Y-%m-%d/%H.mp4
  recordFormat: fmp4
  recordEncryption: aes-256-cbc
  recordEncryptionKey: ${ENCRYPTION_KEY}  # 32 bytes hex
```

### 2. Auditoria de Acesso

```python
# backend/middleware/audit.py
from datetime import datetime
import logging

audit_logger = logging.getLogger('audit')

class AuditMiddleware:
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope['type'] == 'http':
            # Log acesso a playback
            if '/playback/' in scope['path']:
                user = scope.get('user')
                audit_logger.info({
                    'timestamp': datetime.utcnow().isoformat(),
                    'user_id': user.id if user else None,
                    'action': 'playback_access',
                    'path': scope['path'],
                    'ip': scope['client'][0]
                })
        
        await self.app(scope, receive, send)
```

### 3. LGPD Compliance

```sql
-- Tabela de consentimento
CREATE TABLE user_consent (
    user_id INT PRIMARY KEY,
    recording_consent BOOLEAN DEFAULT FALSE,
    consent_date TIMESTAMP,
    ip_address VARCHAR(45),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Tabela de solicitações de exclusão
CREATE TABLE deletion_requests (
    id SERIAL PRIMARY KEY,
    user_id INT,
    request_date TIMESTAMP DEFAULT NOW(),
    status VARCHAR(50), -- 'pending', 'processing', 'completed'
    completed_date TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### 4. Penetration Testing

```bash
# OWASP ZAP scan
docker run -t owasp/zap2docker-stable zap-baseline.py \
  -t https://api.gtvision.com \
  -r zap-report.html

# Nmap scan
nmap -sV -sC -p- api.gtvision.com

# SSL Labs
curl -s "https://api.ssllabs.com/api/v3/analyze?host=api.gtvision.com" | jq
```

---

## SPRINT 20: DOCUMENTAÇÃO E HANDOFF

### Objetivo
Documentação completa e transferência de conhecimento

### 1. Runbook Operacional

```markdown
# GTVision Runbook

## Operações Diárias

### Verificar Saúde do Sistema
```bash
# Health check de todos os nós
for node in $(aws ec2 describe-instances --filters "Name=tag:Name,Values=mediamtx-node" --query 'Reservations[].Instances[].PrivateIpAddress' --output text); do
  curl -s http://$node:9997/v3/config/global/get > /dev/null && echo "✓ $node" || echo "✗ $node"
done
```

### Adicionar Nova Câmera
```bash
curl -X POST http://orchestrator.gtvision.com/cameras/provision \
  -H "Content-Type: application/json" \
  -d '{
    "camera_id": 121,
    "rtsp_url": "rtsp://192.168.1.121/stream",
    "name": "Câmera 121"
  }'
```

### Restaurar Gravação do S3
```bash
./scripts/restore_from_s3.sh 42 2026-02-05
```

## Troubleshooting

### Câmera Não Grava
1. Verificar se câmera está online: `curl http://node:9997/v3/paths/get/cam_42`
2. Verificar logs: `docker logs gtvision_mediamtx | grep cam_42`
3. Verificar disco: `df -h /recordings`

### Playback Não Funciona
1. Verificar se arquivo existe: `ls /recordings/cam_42/2026-02-05/15.mp4`
2. Validar arquivo: `ffprobe /recordings/cam_42/2026-02-05/15.mp4`
3. Verificar logs do MediaMTX

### Disco Cheio
1. Verificar retenção: `grep recordDeleteAfter mediamtx.yml`
2. Forçar limpeza: `find /recordings -mtime +7 -delete`
3. Expandir EBS: `aws ec2 modify-volume --volume-id vol-xxx --size 4000`
```

### 2. Documentação de API

```yaml
# openapi.yml
openapi: 3.0.0
info:
  title: GTVision API
  version: 1.0.0

paths:
  /api/playback/cameras/{camera_id}/timeline:
    get:
      summary: Retorna timeline de gravações
      parameters:
        - name: camera_id
          in: path
          required: true
          schema:
            type: integer
        - name: date
          in: query
          required: true
          schema:
            type: string
            format: date
      responses:
        '200':
          description: Timeline de segmentos
          content:
            application/json:
              schema:
                type: object
                properties:
                  segments:
                    type: array
                    items:
                      type: object
                      properties:
                        start:
                          type: string
                          format: date-time
                        end:
                          type: string
                          format: date-time
                        file_path:
                          type: string
                        size_bytes:
                          type: integer
```

### 3. Treinamento de Equipe

**Tópicos**:
1. Arquitetura do sistema
2. Fluxo de gravação
3. Playback e timeline
4. Operações diárias
5. Troubleshooting
6. Deploy e rollback
7. Monitoramento e alertas

**Duração**: 2 dias (16h)

### Entregáveis Finais

- [ ] Documentação completa (README, runbooks, API docs)
- [ ] Código comentado e limpo
- [ ] Testes automatizados (>80% coverage)
- [ ] Pipeline CI/CD funcional
- [ ] Infraestrutura Terraform
- [ ] Monitoramento e alertas configurados
- [ ] Backup e DR testados
- [ ] Treinamento da equipe concluído
- [ ] Handoff meeting realizado

---

## 🎉 FIM DO MVP

**Status**: Produção  
**Capacidade**: 120 câmeras  
**Uptime**: 99.9%  
**Custo**: ~$2,500/mês  
**Equipe**: Treinada e autônoma
