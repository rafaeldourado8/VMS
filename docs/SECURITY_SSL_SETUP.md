# Configuração SSL e Segurança OWASP - Produção

## 🔐 Implementação Rápida

### 1. Configurar SSL/TLS (15 min)

#### Opção A: AWS Certificate Manager (Recomendado - Grátis)

```bash
# Solicitar certificado SSL
aws acm request-certificate \
  --domain-name your-domain.com \
  --subject-alternative-names www.your-domain.com *.your-domain.com \
  --validation-method DNS \
  --region us-east-1

# Anotar ARN do certificado
# arn:aws:acm:us-east-1:123456789012:certificate/xxxxxxxx

# Adicionar registros DNS para validação
# AWS Console → ACM → Ver detalhes do certificado → Criar registros no Route53
```

#### Opção B: Let's Encrypt (Alternativa)

```bash
# Instalar certbot
sudo apt-get install certbot

# Gerar certificado
sudo certbot certonly --standalone -d your-domain.com -d www.your-domain.com

# Certificados em: /etc/letsencrypt/live/your-domain.com/
# - fullchain.pem
# - privkey.pem
```

### 2. Configurar ALB com SSL (10 min)

```bash
cd terraform/prod
```

Adicionar ao `main.tf`:

```hcl
# HTTPS Listener
resource "aws_lb_listener" "https" {
  load_balancer_arn = aws_lb.main.arn
  port              = "443"
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS-1-2-2017-01"
  certificate_arn   = "arn:aws:acm:us-east-1:123456789012:certificate/xxxxxxxx"
  
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.backend_blue.arn
  }
}

# Redirect HTTP to HTTPS
resource "aws_lb_listener" "http_redirect" {
  load_balancer_arn = aws_lb.main.arn
  port              = "80"
  protocol          = "HTTP"
  
  default_action {
    type = "redirect"
    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }
}
```

Aplicar:

```bash
terraform plan -out=tfplan
terraform apply tfplan
```

### 3. Configurar WAF OWASP (20 min)

```bash
# Criar Web ACL com regras OWASP
aws wafv2 create-web-acl \
  --name vms-prod-waf \
  --scope REGIONAL \
  --region us-east-1 \
  --default-action Allow={} \
  --rules file://waf-rules.json
```

Criar `waf-rules.json`:

```json
[
  {
    "Name": "AWSManagedRulesCommonRuleSet",
    "Priority": 1,
    "Statement": {
      "ManagedRuleGroupStatement": {
        "VendorName": "AWS",
        "Name": "AWSManagedRulesCommonRuleSet"
      }
    },
    "OverrideAction": {
      "None": {}
    },
    "VisibilityConfig": {
      "SampledRequestsEnabled": true,
      "CloudWatchMetricsEnabled": true,
      "MetricName": "AWSManagedRulesCommonRuleSetMetric"
    }
  },
  {
    "Name": "AWSManagedRulesKnownBadInputsRuleSet",
    "Priority": 2,
    "Statement": {
      "ManagedRuleGroupStatement": {
        "VendorName": "AWS",
        "Name": "AWSManagedRulesKnownBadInputsRuleSet"
      }
    },
    "OverrideAction": {
      "None": {}
    },
    "VisibilityConfig": {
      "SampledRequestsEnabled": true,
      "CloudWatchMetricsEnabled": true,
      "MetricName": "AWSManagedRulesKnownBadInputsRuleSetMetric"
    }
  },
  {
    "Name": "AWSManagedRulesSQLiRuleSet",
    "Priority": 3,
    "Statement": {
      "ManagedRuleGroupStatement": {
        "VendorName": "AWS",
        "Name": "AWSManagedRulesSQLiRuleSet"
      }
    },
    "OverrideAction": {
      "None": {}
    },
    "VisibilityConfig": {
      "SampledRequestsEnabled": true,
      "CloudWatchMetricsEnabled": true,
      "MetricName": "AWSManagedRulesSQLiRuleSetMetric"
    }
  },
  {
    "Name": "RateLimitRule",
    "Priority": 4,
    "Statement": {
      "RateBasedStatement": {
        "Limit": 2000,
        "AggregateKeyType": "IP"
      }
    },
    "Action": {
      "Block": {}
    },
    "VisibilityConfig": {
      "SampledRequestsEnabled": true,
      "CloudWatchMetricsEnabled": true,
      "MetricName": "RateLimitRuleMetric"
    }
  }
]
```

Associar WAF ao ALB:

```bash
aws wafv2 associate-web-acl \
  --web-acl-arn arn:aws:wafv2:us-east-1:123456789012:regional/webacl/vms-prod-waf/xxxxxxxx \
  --resource-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/vms-prod-alb/xxxxxxxx \
  --region us-east-1
```

### 4. Configurar Django Security Settings (10 min)

Atualizar `backend/settings.py`:

```python
# Security Settings
DEBUG = False
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

# HTTPS/SSL
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Security Headers
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# CORS
CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', '').split(',')
CORS_ALLOW_CREDENTIALS = True

# CSP
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'")
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")
CSP_IMG_SRC = ("'self'", "data:", "https:")
CSP_CONNECT_SRC = ("'self'", "wss:")

# Rate Limiting
RATELIMIT_ENABLE = True
RATELIMIT_USE_CACHE = 'default'

# Session Security
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'
SESSION_COOKIE_AGE = 3600

# Password Validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 12}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]
```

### 5. Configurar Secrets Manager (15 min)

```bash
# Criar secrets
aws secretsmanager create-secret \
  --name vms/prod/database \
  --secret-string '{"username":"gtvision_user","password":"STRONG_PASSWORD_HERE"}' \
  --region us-east-1

aws secretsmanager create-secret \
  --name vms/prod/django \
  --secret-string '{"secret_key":"DJANGO_SECRET_KEY_HERE","jwt_secret":"JWT_SECRET_HERE"}' \
  --region us-east-1

aws secretsmanager create-secret \
  --name vms/prod/redis \
  --secret-string '{"auth_token":"REDIS_AUTH_TOKEN_HERE"}' \
  --region us-east-1
```

### 6. Atualizar ECS Task Definition (10 min)

```json
{
  "family": "vms-prod-backend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "2048",
  "memory": "4096",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "123456789012.dkr.ecr.us-east-1.amazonaws.com/vms/backend:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "secrets": [
        {
          "name": "SECRET_KEY",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789012:secret:vms/prod/django:secret_key::"
        },
        {
          "name": "DB_PASSWORD",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789012:secret:vms/prod/database:password::"
        },
        {
          "name": "REDIS_PASSWORD",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789012:secret:vms/prod/redis:auth_token::"
        }
      ],
      "environment": [
        {"name": "DEBUG", "value": "False"},
        {"name": "SECURE_SSL_REDIRECT", "value": "True"},
        {"name": "ALLOWED_HOSTS", "value": "your-domain.com,www.your-domain.com"}
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/aws/ecs/vms-prod-backend",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ],
  "executionRoleArn": "arn:aws:iam::123456789012:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::123456789012:role/ecsTaskRole"
}
```

### 7. Testar Segurança (10 min)

```bash
# Testar SSL
curl -I https://your-domain.com

# Verificar headers de segurança
curl -I https://your-domain.com | grep -E "Strict-Transport-Security|X-Frame-Options|X-Content-Type-Options"

# Testar rate limiting
for i in {1..100}; do curl https://your-domain.com/api/health/; done

# Scan de vulnerabilidades
nmap --script ssl-enum-ciphers -p 443 your-domain.com
```

### 8. Configurar Monitoring (10 min)

```bash
# Criar alarmes de segurança
aws cloudwatch put-metric-alarm \
  --alarm-name vms-prod-waf-blocked-requests \
  --alarm-description "Alert on blocked requests" \
  --metric-name BlockedRequests \
  --namespace AWS/WAFV2 \
  --statistic Sum \
  --period 300 \
  --threshold 100 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 1

# Habilitar GuardDuty
aws guardduty create-detector --enable --region us-east-1

# Habilitar Security Hub
aws securityhub enable-security-hub --region us-east-1
```

## ✅ Checklist de Segurança OWASP

### A01:2021 – Broken Access Control
- [x] Implementar autenticação JWT
- [x] Validar permissões em todas as rotas
- [x] Rate limiting por IP
- [x] Session timeout configurado

### A02:2021 – Cryptographic Failures
- [x] SSL/TLS habilitado (TLS 1.2+)
- [x] HSTS configurado
- [x] Secrets no AWS Secrets Manager
- [x] Dados sensíveis criptografados

### A03:2021 – Injection
- [x] Django ORM (queries parametrizadas)
- [x] WAF com proteção SQL Injection
- [x] Input validation
- [x] Output encoding

### A04:2021 – Insecure Design
- [x] Arquitetura Multi-AZ
- [x] Backup automático
- [x] Disaster recovery plan
- [x] Security by design

### A05:2021 – Security Misconfiguration
- [x] DEBUG=False
- [x] Secrets externalizados
- [x] Security headers configurados
- [x] Portas desnecessárias fechadas

### A06:2021 – Vulnerable Components
- [x] Dependências atualizadas
- [x] Scan de vulnerabilidades (Dependabot)
- [x] Container scanning
- [x] Regular updates

### A07:2021 – Authentication Failures
- [x] Password policy forte (12+ chars)
- [x] Account lockout (5 tentativas)
- [x] MFA disponível
- [x] Session management seguro

### A08:2021 – Software and Data Integrity
- [x] Code signing
- [x] CI/CD com validação
- [x] Integrity checks
- [x] Audit logs

### A09:2021 – Logging Failures
- [x] CloudWatch Logs habilitado
- [x] Audit trail completo
- [x] Alertas configurados
- [x] Log retention 30 dias

### A10:2021 – Server-Side Request Forgery
- [x] URL validation
- [x] Network segmentation
- [x] WAF rules
- [x] Egress filtering

## 🎯 Comandos Rápidos

```bash
# Deploy com segurança
cd terraform/prod
terraform apply -var="enable_waf=true" -var="enable_ssl=true"

# Verificar SSL
openssl s_client -connect your-domain.com:443 -tls1_2

# Testar OWASP
docker run -t owasp/zap2docker-stable zap-baseline.py -t https://your-domain.com

# Audit de segurança
aws inspector2 enable --resource-types ECR,EC2,LAMBDA
```

## 📊 Custos Adicionais

- **ACM Certificate**: Grátis
- **WAF**: ~$5/mês + $1 por milhão de requests
- **Shield Standard**: Grátis
- **GuardDuty**: ~$4.50/mês
- **Security Hub**: ~$1.20/mês

**Total adicional: ~$12/mês**

## 🆘 Troubleshooting

### SSL não funciona
```bash
# Verificar certificado ACM
aws acm describe-certificate --certificate-arn arn:aws:acm:...

# Verificar listener HTTPS
aws elbv2 describe-listeners --load-balancer-arn arn:aws:elasticloadbalancing:...
```

### WAF bloqueando tráfego legítimo
```bash
# Ver logs WAF
aws wafv2 get-sampled-requests --web-acl-arn ... --rule-metric-name ...

# Ajustar regras
aws wafv2 update-web-acl --id ... --scope REGIONAL
```

Pronto para deploy seguro! 🔐
