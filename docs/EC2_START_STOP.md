# Gerenciar EC2 Spot - Ligar/Desligar

## 💰 Economia

**Custos por hora:**
- t3.xlarge Spot: ~$0.03/hora
- EBS 100GB: $0.011/hora (~$8/mês fixo)

**Exemplos:**
- 8h/dia, 5 dias/semana = ~$5/mês + $8 EBS = **$13/mês**
- 24/7 = ~$22/mês + $8 EBS = **$30/mês**

**Você só paga pela instância quando ela está LIGADA!**

---

## Via AWS Console (Mais Fácil)

### Desligar
1. AWS Console → EC2 → Instances
2. Selecionar instância `vms-dev-spot`
3. Instance state → **Stop instance**
4. ✅ Confirmar

### Ligar
1. AWS Console → EC2 → Instances
2. Selecionar instância `vms-dev-spot`
3. Instance state → **Start instance**
4. ⚠️ **IP público muda!** Anotar novo IP

---

## Via AWS CLI (Mais Rápido)

### Desligar
```bash
aws ec2 stop-instances --instance-ids i-XXXXXXXXX
```

### Ligar
```bash
aws ec2 start-instances --instance-ids i-XXXXXXXXX
```

### Ver status e IP
```bash
aws ec2 describe-instances --instance-ids i-XXXXXXXXX \
  --query 'Reservations[0].Instances[0].[State.Name,PublicIpAddress]' \
  --output text
```

---

## Scripts Prontos

### `scripts/aws/stop-dev.sh`
```bash
#!/bin/bash
INSTANCE_ID="i-XXXXXXXXX"  # Substituir pelo seu ID

echo "Parando instância $INSTANCE_ID..."
aws ec2 stop-instances --instance-ids $INSTANCE_ID

echo "✓ Instância sendo desligada"
echo "Economia: ~$0.03/hora"
```

### `scripts/aws/start-dev.sh`
```bash
#!/bin/bash
INSTANCE_ID="i-XXXXXXXXX"  # Substituir pelo seu ID

echo "Iniciando instância $INSTANCE_ID..."
aws ec2 start-instances --instance-ids $INSTANCE_ID

echo "Aguardando iniciar..."
aws ec2 wait instance-running --instance-ids $INSTANCE_ID

NEW_IP=$(aws ec2 describe-instances --instance-ids $INSTANCE_ID \
  --query 'Reservations[0].Instances[0].PublicIpAddress' \
  --output text)

echo ""
echo "✓ Instância iniciada!"
echo "Novo IP: $NEW_IP"
echo ""
echo "Conectar:"
echo "ssh -i vms-dev-key.pem ubuntu@$NEW_IP"
echo ""
echo "Aguarde 1-2 minutos para Docker iniciar"
```

---

## ⚠️ Importante: IP Público Muda

Toda vez que você **desliga e liga**, o IP público muda!

### Solução 1: Elastic IP (Recomendado)
**Custo:** GRÁTIS se associado, $0.005/hora se não associado

```bash
# Alocar IP fixo (uma vez)
aws ec2 allocate-address --domain vpc

# Anotar Allocation ID: eipalloc-XXXXXXXXX

# Associar à instância
aws ec2 associate-address \
  --instance-id i-XXXXXXXXX \
  --allocation-id eipalloc-XXXXXXXXX
```

**Vantagens:**
- ✅ IP nunca muda
- ✅ Grátis quando instância está ligada
- ✅ Não precisa reconfigurar nada

**Desvantagem:**
- ❌ Cobra $0.005/hora (~$3.60/mês) quando instância está DESLIGADA

### Solução 2: Atualizar IP Manualmente
Toda vez que ligar, atualizar:
- GitHub Secrets (`DEV_SERVER_IP`)
- `.env` no servidor (`DJANGO_ALLOWED_HOSTS`)

---

## Rotina Recomendada

### Desenvolvimento Ativo (Segunda a Sexta)
```bash
# Manhã (9h)
bash scripts/aws/start-dev.sh

# Trabalhar...

# Noite (18h)
bash scripts/aws/stop-dev.sh
```

**Economia:** ~$13/mês vs $30/mês (56% de economia)

### Fim de Semana
Deixar desligado = **$0**

---

## Automação com Cron (Opcional)

### No seu computador local

**Ligar automaticamente às 9h (dias úteis):**
```bash
# crontab -e
0 9 * * 1-5 /path/to/scripts/aws/start-dev.sh
```

**Desligar automaticamente às 18h:**
```bash
0 18 * * 1-5 /path/to/scripts/aws/stop-dev.sh
```

---

## Automação com Lambda (Avançado)

### Lambda para ligar/desligar em horários

**Custo:** GRÁTIS (dentro do free tier)

```python
# lambda_start_instance.py
import boto3

def lambda_handler(event, context):
    ec2 = boto3.client('ec2')
    ec2.start_instances(InstanceIds=['i-XXXXXXXXX'])
    return {'statusCode': 200, 'body': 'Instance started'}
```

**EventBridge Rules:**
- Ligar: `cron(0 9 ? * MON-FRI *)` (9h UTC, seg-sex)
- Desligar: `cron(0 18 ? * MON-FRI *)` (18h UTC, seg-sex)

---

## Checklist ao Desligar

Antes de desligar:
- [ ] Commit e push do código
- [ ] Backup manual se necessário: `bash scripts/backup_db.sh`
- [ ] Verificar se não há processos críticos rodando

---

## Checklist ao Ligar

Depois de ligar:
- [ ] Anotar novo IP (se não usar Elastic IP)
- [ ] Aguardar 1-2 minutos para Docker iniciar
- [ ] Testar: `curl http://NOVO_IP/api/health/`
- [ ] Atualizar GitHub Secrets se IP mudou

---

## FAQ

**P: Perco os dados ao desligar?**
R: NÃO! O volume EBS persiste. Todos os dados ficam salvos.

**P: Quanto tempo demora para ligar?**
R: ~30-60 segundos para instância + 1-2 minutos para Docker iniciar.

**P: E se a AWS terminar minha Spot Instance?**
R: Configure `DeleteOnTermination: false` no EBS. Você pode criar nova instância e anexar o mesmo volume.

**P: Posso usar hibernação?**
R: Sim, mas Spot Instances não suportam hibernação. Use Stop/Start.

**P: Vale a pena Elastic IP?**
R: SIM! Se você liga/desliga frequentemente. Economiza tempo e evita reconfiguração.

---

## Comparação de Custos

### Sem Elastic IP
| Uso | Custo EC2 | Custo EBS | Total/mês |
|-----|-----------|-----------|-----------|
| 24/7 | $22 | $8 | $30 |
| 8h/dia útil | $5 | $8 | $13 |
| 4h/dia útil | $2.50 | $8 | $10.50 |

### Com Elastic IP
| Uso | Custo EC2 | Custo EBS | Custo EIP | Total/mês |
|-----|-----------|-----------|-----------|-----------|
| 24/7 | $22 | $8 | $0 | $30 |
| 8h/dia útil | $5 | $8 | $2.40 | $15.40 |
| 4h/dia útil | $2.50 | $8 | $3 | $13.50 |

**Conclusão:** Elastic IP vale a pena se usar >16h/dia. Caso contrário, IP dinâmico é mais barato.

---

## Comandos Rápidos

```bash
# Ver quanto tempo está ligada
aws ec2 describe-instances --instance-ids i-XXXXXXXXX \
  --query 'Reservations[0].Instances[0].LaunchTime'

# Ver custo estimado (CloudWatch)
aws ce get-cost-and-usage \
  --time-period Start=2024-01-01,End=2024-01-31 \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --filter file://filter.json
```

---

## Recomendação Final

**Para desenvolvimento:**
1. ✅ Use Elastic IP ($0 quando ligada)
2. ✅ Desligue quando não usar
3. ✅ Automatize com scripts
4. ✅ Backup antes de desligar

**Economia esperada:** 50-70% vs deixar ligada 24/7
