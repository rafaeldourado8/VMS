# 🔒 Segurança e Compliance - VMS

**Versão:** 1.0  
**Data:** Janeiro 2026  
**Status:** ⚠️ CRÍTICO - Implementar ANTES da IA

---

## ⚠️ Por que implementar AGORA?

**Para prefeituras:**
- ✅ LGPD obrigatória (Lei 13.709/2018) - Multa até R$ 50 milhões ou 2% do faturamento
- ✅ Dados sensíveis (imagens de pessoas)
- ✅ Responsabilidade civil e criminal
- ✅ Auditoria externa obrigatória

**Custo de implementar depois:** 10x maior + risco legal + reputação

---

## 🛡️ OWASP Top 10 - Mitigações Obrigatórias

### **A01: Broken Access Control** ⚠️ CRÍTICO

**Risco:** Usuário comum acessar câmeras restritas ou gravações de outras áreas.

**Implementação:**
```python
# apps/cameras/permissions.py
from rest_framework import permissions
from django.utils import timezone

class CameraAccessPermission(permissions.BasePermission):
    """Usuário só acessa câmeras do seu setor"""
    def has_object_permission(self, request, view, obj):
        return obj.sector in request.user.sectors.all()

class RecordingAccessPermission(permissions.BasePermission):
    """Log obrigatório para acesso a gravações (LGPD Art. 37)"""
    def has_object_permission(self, request, view, obj):
        AccessLog.objects.create(
            user=request.user,
            camera=obj.camera,
            action='view_recording',
            timestamp=timezone.now(),
            ip_address=request.META.get('REMOTE_ADDR')
        )
        return obj.camera.sector in request.user.sectors.all()

# apps/cameras/views.py
class CameraViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, CameraAccessPermission]
    
    def get_queryset(self):
        # NUNCA retorne todas as câmeras
        return Camera.objects.filter(
            sector__in=self.request.user.sectors.all()
        )
```

**Checklist:**
- [ ] Permissões por setor/departamento implementadas
- [ ] Log de acesso a gravações funcionando
- [ ] Validação server-side em TODAS as requisições
- [ ] Teste: usuário do setor A não acessa câmera do setor B

---

### **A02: Cryptographic Failures** ⚠️ CRÍTICO

**Risco:** Gravações vazadas, credenciais expostas.

**Implementação:**
```python
# config/settings.py

# 1. HTTPS obrigatório em produção
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000  # 1 ano
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# 2. Criptografia de credenciais RTSP
from cryptography.fernet import Fernet

ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY')  # Gerar: Fernet.generate_key()

# apps/cameras/models.py
class Camera(models.Model):
    rtsp_url_encrypted = models.CharField(max_length=500)
    
    def set_rtsp_url(self, url):
        cipher = Fernet(settings.ENCRYPTION_KEY)
        self.rtsp_url_encrypted = cipher.encrypt(url.encode()).decode()
    
    def get_rtsp_url(self):
        cipher = Fernet(settings.ENCRYPTION_KEY)
        return cipher.decrypt(self.rtsp_url_encrypted.encode()).decode()

# 3. Gravações criptografadas no S3
AWS_S3_ENCRYPTION = 'AES256'
AWS_S3_OBJECT_PARAMETERS = {
    'ServerSideEncryption': 'AES256',
}
```

**Checklist:**
- [ ] HTTPS configurado (certificado válido)
- [ ] Credenciais RTSP criptografadas no banco
- [ ] Gravações criptografadas no S3 (AES-256)
- [ ] Secrets em variáveis de ambiente (nunca no código)
- [ ] Rotação de chaves a cada 90 dias

---

### **A03: Injection** ⚠️ CRÍTICO

**Risco:** SQL Injection, Command Injection.

**Implementação:**
```python
# ❌ NUNCA FAÇA ISSO
Camera.objects.raw(f"SELECT * FROM cameras WHERE name = '{user_input}'")

# ✅ SEMPRE USE ORM
Camera.objects.filter(name=user_input)

# Para MediaMTX API
def create_mediamtx_path(camera_id, rtsp_url):
    # Sanitiza entrada
    camera_id = int(camera_id)  # Força tipo
    
    # Valida URL RTSP
    if not rtsp_url.startswith('rtsp://'):
        raise ValueError("URL RTSP inválida")
    
    # Usa biblioteca, não shell
    response = requests.post(
        f"{settings.MEDIAMTX_API}/v3/config/paths/add/cam_{camera_id}",
        json={'source': rtsp_url},  # JSON é seguro
        timeout=5
    )
    return response.json()
```

**Checklist:**
- [ ] Zero raw SQL queries no código
- [ ] Validação de entrada em TODOS os endpoints
- [ ] Sanitização de nomes de arquivo (gravações)
- [ ] Teste: tentar SQL injection em busca de câmeras

---

### **A04: Insecure Design**

**Risco:** Arquitetura permite ataques por design.

**Implementação:**
```python
# 1. Rate limiting (previne brute force)
from django_ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='5/m', method='POST')
def login_view(request):
    """Máximo 5 tentativas de login por minuto"""
    pass

# 2. Timeout em TODAS as operações externas
requests.get(url, timeout=5)  # SEMPRE com timeout

# 3. Princípio do menor privilégio
class User(AbstractUser):
    role = models.CharField(max_length=20, choices=[
        ('operator', 'Operador'),      # Só visualiza
        ('supervisor', 'Supervisor'),  # Visualiza + exporta
        ('admin', 'Administrador'),    # Tudo
    ])
    sectors = models.ManyToManyField('Sector')
```

**Checklist:**
- [ ] Rate limiting em login e APIs públicas
- [ ] Timeout em todas as chamadas externas
- [ ] Roles com menor privilégio possível
- [ ] Teste: tentar 100 logins em 1 minuto (deve bloquear)

---

### **A05: Security Misconfiguration** ⚠️ CRÍTICO

**Risco:** Debug ativo, senhas padrão, portas expostas.

**Implementação:**
```python
# config/settings.py (PRODUÇÃO)
DEBUG = False
ALLOWED_HOSTS = ['vms.prefeitura.gov.br']
SECRET_KEY = os.getenv('SECRET_KEY')  # Nunca hardcode

# Admin em URL customizada (dificulta ataques)
if not DEBUG:
    urlpatterns = [
        path('painel-admin-seguro/', admin.site.urls),
    ]

# Headers de segurança
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = 'same-origin'
```

**docker-compose.yml (PRODUÇÃO):**
```yaml
services:
  backend:
    expose:
      - "8000"  # ✅ Apenas interno
    # NÃO use ports: - "8000:8000"  # ❌ Exposto
  
  postgres:
    environment:
      POSTGRES_PASSWORD: ${DB_PASSWORD}  # Nunca hardcode
    # NÃO exponha: ports: - "5432:5432"  # ❌ PERIGO
  
  mediamtx:
    environment:
      MTX_PROTOCOLS: "tcp"
      MTX_RTSP_AUTH_METHODS: "basic"
```

**Checklist:**
- [ ] DEBUG=False em produção
- [ ] Senhas fortes e únicas (mínimo 16 caracteres)
- [ ] Admin em URL customizada
- [ ] Portas internas não expostas
- [ ] Scan: `docker scan vms-backend` e `safety check`

---

### **A07: Identification and Authentication Failures** ⚠️ CRÍTICO

**Risco:** Sessões roubadas, senhas fracas, acesso não autorizado.

**Implementação:**
```python
# config/settings.py

# 1. Senhas fortes obrigatórias
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 12}
    },
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
]

# 2. Sessão segura com TIMEOUT DE 3 MINUTOS
SESSION_COOKIE_AGE = 180  # 3 minutos (180 segundos)
SESSION_SAVE_EVERY_REQUEST = True  # Renova a cada request
SESSION_COOKIE_HTTPONLY = True  # Não acessível via JavaScript
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_SAMESITE = 'Strict'

# 3. MFA obrigatório para administradores
INSTALLED_APPS += ['django_otp', 'django_otp.plugins.otp_totp']

from django_otp.decorators import otp_required

@otp_required
def admin_view(request):
    pass

# 4. Bloqueio após tentativas falhas
INSTALLED_APPS += ['axes']
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = timedelta(minutes=30)
AXES_LOCKOUT_TEMPLATE = 'account_locked.html'
```

**Frontend: Logout automático após 3 minutos de inatividade**
```typescript
// src/utils/sessionTimeout.ts
let inactivityTimer: NodeJS.Timeout;

export function setupSessionTimeout() {
  const TIMEOUT = 3 * 60 * 1000; // 3 minutos em milissegundos
  
  function resetTimer() {
    clearTimeout(inactivityTimer);
    inactivityTimer = setTimeout(() => {
      // Logout automático
      localStorage.removeItem('token');
      sessionStorage.clear();
      window.location.href = '/login?timeout=true';
    }, TIMEOUT);
  }
  
  // Eventos que resetam o timer (atividade do usuário)
  const events = ['mousedown', 'keypress', 'scroll', 'touchstart', 'click'];
  events.forEach(event => {
    document.addEventListener(event, resetTimer, true);
  });
  
  resetTimer(); // Inicia o timer
}

// src/App.tsx
import { setupSessionTimeout } from './utils/sessionTimeout';

function App() {
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      setupSessionTimeout();
    }
  }, []);
  
  return <Router>...</Router>;
}
```

**Checklist:**
- [ ] Senhas com mínimo 12 caracteres
- [ ] MFA para administradores
- [ ] Bloqueio após 5 tentativas falhas
- [ ] **Logout automático após 3 minutos de inatividade**
- [ ] Teste: deixar sistema parado por 3 minutos (deve deslogar)

---

### **A09: Security Logging and Monitoring Failures** ⚠️ CRÍTICO

**Risco:** Ataque não detectado, sem evidências para auditoria.

**Implementação:**
```python
# apps/core/middleware.py
import logging
from django.utils import timezone

security_logger = logging.getLogger('security')

class SecurityAuditMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Log TODAS as ações sensíveis
        if request.path.startswith('/api/cameras/') or \
           request.path.startswith('/api/recordings/'):
            security_logger.info({
                'user': request.user.username if request.user.is_authenticated else 'anonymous',
                'ip': request.META.get('REMOTE_ADDR'),
                'action': f"{request.method} {request.path}",
                'timestamp': timezone.now().isoformat(),
                'user_agent': request.META.get('HTTP_USER_AGENT'),
            })
        
        response = self.get_response(request)
        
        # Alerta em ações suspeitas
        if response.status_code == 403:
            security_logger.warning(
                f"Acesso negado: {request.user} tentou acessar {request.path}"
            )
        
        return response

# apps/core/models.py
class AuditLog(models.Model):
    """Log de auditoria imutável (LGPD)"""
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    action = models.CharField(max_length=100)
    resource = models.CharField(max_length=200)
    ip_address = models.GenericIPAddressField()
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.JSONField()
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action', 'timestamp']),
        ]
        # Impede deleção (append-only)
        permissions = [('view_auditlog', 'Can view audit log')]
```

**Logs obrigatórios (LGPD Art. 37):**
- ✅ Acesso a gravações (quem, quando, qual câmera)
- ✅ Exportação de vídeos
- ✅ Alteração de configurações
- ✅ Login/logout
- ✅ Tentativas de acesso negado

**Checklist:**
- [ ] Log de todas as ações sensíveis
- [ ] Logs imutáveis (append-only)
- [ ] Retenção de logs por 1 ano (mínimo)
- [ ] Alertas em tempo real para ações suspeitas
- [ ] Dashboard de auditoria para compliance

---

## 📋 Compliance: LGPD

### **Requisitos Obrigatórios**

#### **1. Base Legal (Art. 7º)**
```python
# apps/cameras/models.py
class Camera(models.Model):
    is_public_area = models.BooleanField(
        default=True,
        help_text="Câmera em área pública (não requer consentimento)"
    )
    consent_required = models.BooleanField(default=False)
    privacy_notice_url = models.URLField(
        blank=True,
        help_text="URL do aviso de privacidade"
    )
```

#### **2. Direitos dos Titulares (Art. 18)**
```python
# apps/lgpd/views.py
class LGPDRequestViewSet(viewsets.ViewSet):
    @action(detail=False, methods=['post'])
    def request_deletion(self, request):
        """Titular solicita exclusão de imagens (Art. 18, III)"""
        LGPDRequest.objects.create(
            requester_cpf=request.data['cpf'],
            request_type='deletion',
            camera_ids=request.data['cameras'],
            date_range=request.data['date_range'],
            status='pending'
        )
        # Prazo legal: 15 dias para responder
        return Response({
            'message': 'Solicitação registrada. Prazo de resposta: 15 dias úteis.'
        })
```

#### **3. RIPD - Relatório de Impacto (Art. 38)**
```markdown
# RIPD - Relatório de Impacto à Proteção de Dados

## 1. Dados Coletados
- Imagens de vídeo (dados pessoais sensíveis - Art. 5º, II)
- Placas de veículos
- Localização e horário das capturas

## 2. Finalidade
- Segurança pública (Art. 7º, III)
- Investigação de crimes (Art. 7º, II)

## 3. Medidas de Segurança Técnicas
- Criptografia em trânsito (TLS 1.3)
- Criptografia em repouso (AES-256)
- Acesso restrito por função (RBAC)
- Logs de auditoria imutáveis
- Retenção limitada (90 dias)
- **Logout automático após 3 minutos de inatividade**
- MFA para administradores
- Rate limiting e proteção contra brute force

## 4. Medidas de Segurança Organizacionais
- DPO nomeado
- Treinamento da equipe
- Política de privacidade publicada
- Processo para exercício de direitos

## 5. Compartilhamento de Dados
- Apenas com autoridades competentes mediante ordem judicial
- Contratos de processamento com fornecedores (AWS)

## 6. Riscos Identificados
- Vazamento de imagens: MITIGADO (criptografia + acesso restrito)
- Acesso não autorizado: MITIGADO (MFA + logs + timeout)
- Retenção excessiva: MITIGADO (exclusão automática após 90 dias)
```

**Checklist LGPD:**
- [ ] DPO (Encarregado) nomeado
- [ ] Política de privacidade publicada
- [ ] Processo para exercício de direitos implementado
- [ ] RIPD documentado
- [ ] Contratos com fornecedores (AWS, etc)
- [ ] Treinamento da equipe realizado

---

## 🔐 Hardening de Infraestrutura

### **1. Firewall (UFW)**
```bash
# Configuração mínima
ufw default deny incoming
ufw default allow outgoing
ufw allow 443/tcp   # HTTPS
ufw allow 22/tcp    # SSH (apenas IPs confiáveis)
ufw enable

# Restringir SSH a IPs específicos
ufw allow from 192.168.1.0/24 to any port 22
```

### **2. Fail2ban**
```ini
# /etc/fail2ban/jail.local
[django-auth]
enabled = true
filter = django-auth
logpath = /var/log/vms/security.log
maxretry = 5
bantime = 3600
findtime = 600
```

### **3. Backup Criptografado**
```python
# apps/core/tasks.py
import gnupg
import subprocess
from datetime import date

@shared_task
def backup_database():
    """Backup diário criptografado"""
    # 1. Dump do banco
    subprocess.run([
        'pg_dump', 'vms_db', '-f', '/tmp/backup.sql'
    ], check=True)
    
    # 2. Criptografa com GPG
    gpg = gnupg.GPG()
    with open('/tmp/backup.sql', 'rb') as f:
        gpg.encrypt_file(
            f,
            recipients=['admin@prefeitura.gov.br'],
            output='/tmp/backup.sql.gpg'
        )
    
    # 3. Upload para S3 (criptografado)
    s3_client.upload_file(
        '/tmp/backup.sql.gpg',
        'vms-backups',
        f'backup-{date.today()}.sql.gpg',
        ExtraArgs={'ServerSideEncryption': 'AES256'}
    )
    
    # 4. Remove arquivos locais
    os.remove('/tmp/backup.sql')
    os.remove('/tmp/backup.sql.gpg')
```

---

## 🧪 Testes de Segurança Obrigatórios

```bash
# 1. Scan de vulnerabilidades em containers
docker scan vms-backend:latest

# 2. Scan de dependências Python
safety check --file requirements.txt
pip-audit

# 3. Teste de penetração básico
nmap -sV -sC vms.prefeitura.gov.br
nikto -h https://vms.prefeitura.gov.br

# 4. OWASP ZAP (automatizado)
zap-cli quick-scan https://vms.prefeitura.gov.br

# 5. Testes de segurança automatizados
pytest tests/security/ -v
```

**Checklist de Testes:**
- [ ] Scan de vulnerabilidades (sem HIGH/CRITICAL)
- [ ] Teste de SQL injection
- [ ] Teste de XSS
- [ ] Teste de CSRF
- [ ] Teste de brute force (deve bloquear)
- [ ] Teste de acesso não autorizado
- [ ] Teste de escalação de privilégios
- [ ] **Teste de timeout de 3 minutos**

---

## 📦 Dependências de Segurança

```txt
# requirements-security.txt
django-axes==6.1.1          # Proteção contra brute force
django-ratelimit==4.1.0     # Rate limiting
django-otp==1.3.0           # MFA (Two-Factor Authentication)
qrcode==7.4.2               # QR codes para MFA
cryptography==41.0.7        # Criptografia
django-cors-headers==4.3.1  # CORS seguro
django-csp==3.8             # Content Security Policy
python-gnupg==0.5.1         # Backup criptografado
```

---

## ✅ Checklist Final de Segurança

### **Aplicação**
- [ ] HTTPS obrigatório (certificado válido)
- [ ] DEBUG=False em produção
- [ ] Senhas fortes obrigatórias (12+ caracteres)
- [ ] MFA para administradores
- [ ] Rate limiting ativo
- [ ] Permissões por setor implementadas
- [ ] Logs de auditoria funcionando
- [ ] Credenciais criptografadas no banco
- [ ] **Logout automático após 3 minutos de inatividade**

### **Infraestrutura**
- [ ] Firewall configurado (apenas portas necessárias)
- [ ] Fail2ban ativo
- [ ] Portas internas não expostas
- [ ] Backup criptografado e testado
- [ ] Secrets em variáveis de ambiente

### **Compliance**
- [ ] Política de privacidade publicada
- [ ] RIPD documentado
- [ ] DPO nomeado
- [ ] Processo LGPD implementado
- [ ] Contratos com fornecedores assinados

### **Testes**
- [ ] Scan de vulnerabilidades (sem críticas)
- [ ] Teste de penetração realizado
- [ ] Teste de SQL injection
- [ ] Teste de brute force
- [ ] Teste de acesso não autorizado
- [ ] **Teste de timeout de 3 minutos**

---

## 🚨 Plano de Resposta a Incidentes

### **Fluxo de Resposta**

**1. Detecção (< 5 minutos)**
- Alertas automáticos via Prometheus
- Notificação imediata no Telegram

**2. Contenção (< 15 minutos)**
```bash
# Bloquear IP atacante
ufw deny from <IP_ATACANTE>

# Revogar todas as sessões ativas
python manage.py clearsessions

# Desativar usuário comprometido
python manage.py shell -c "User.objects.filter(username='X').update(is_active=False)"
```

**3. Investigação (< 1 hora)**
- Análise de logs de auditoria
- Identificação de escopo do incidente
- Documentação de evidências

**4. Recuperação (< 4 horas)**
- Restauração de backup se necessário
- Rotação de credenciais comprometidas
- Patch de vulnerabilidade explorada

**5. Comunicação (< 24 horas)**
- Notificação à ANPD (se vazamento de dados)
- Comunicação aos titulares afetados (Art. 48 LGPD)
- Relatório interno para gestão

---

## 📞 Contatos de Emergência

```
DPO: dpo@prefeitura.gov.br
Segurança TI: seguranca@prefeitura.gov.br
ANPD: https://www.gov.br/anpd
Telefone ANPD: 0800-xxx-xxxx
```

---

## 📝 Próximos Passos

**Após implementação:**

1. [ ] Treinar equipe em boas práticas de segurança
2. [ ] Realizar auditoria externa de segurança
3. [ ] Documentar procedimentos operacionais
4. [ ] Configurar alertas de segurança
5. [ ] Agendar revisão trimestral de segurança

---

**Documento aprovado para implementação:** ⬜  
**Data de aprovação:** ___/___/______  
**Responsável técnico:** _________________  
**DPO:** _________________  
**Auditor externo:** _________________
