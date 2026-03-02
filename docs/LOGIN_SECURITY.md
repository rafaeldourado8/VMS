# Segurança do Login - GT-Vision VMS

## ✅ Implementado (Localhost)

### 1. Políticas de Senha Forte
- ✅ Mínimo 8 caracteres
- ✅ Letra maiúscula obrigatória
- ✅ Letra minúscula obrigatória
- ✅ Número obrigatório
- ✅ Caractere especial obrigatório
- ✅ Validação no backend (Django validators)

### 2. Proteção contra Brute Force
- ✅ **Rate Limiting**: 5 tentativas por minuto por IP
- ✅ **Account Lockout**: Bloqueio de 5 minutos após 5 tentativas falhas
- ✅ **Contador de tentativas**: Mostra tentativas restantes
- ✅ **Cache Redis**: Armazena tentativas e lockouts

### 3. Gerenciamento de Sessão Seguro
- ✅ **Access Token**: 15 minutos (reduzido de 60min)
- ✅ **Refresh Token**: 1 dia (reduzido de 7 dias)
- ✅ **Token Rotation**: Tokens renovados automaticamente
- ✅ **Blacklist**: Tokens antigos invalidados
- ✅ **Session Timeout**: 15 minutos de inatividade

### 4. Segurança de Dados
- ✅ **HTTPS Ready**: Configurado para produção
- ✅ **Password Hashing**: Django usa PBKDF2 (seguro)
- ✅ **SQL Injection**: Django ORM protege automaticamente
- ✅ **XSS Protection**: Headers de segurança configurados
- ✅ **CSRF Protection**: Tokens CSRF habilitados

### 5. Boas Práticas UI/UX
- ✅ **Mensagens genéricas**: "Credenciais inválidas" (não revela se é user ou senha)
- ✅ **Feedback de tentativas**: Mostra quantas tentativas restam
- ✅ **Máscara de senha**: Input type="password"

### 6. Auditoria e Logs
- ✅ **LoginLog**: Registra todos os logins (IP, user agent, timestamp)
- ✅ **Email para admins**: Notifica quando alguém loga
- ✅ **Logs de falhas**: Registra tentativas falhas

## 🔄 Performance

### Login otimizado para < 2s:
- ✅ Cache Redis para lockout (rápido)
- ✅ Índices no banco (login_logs)
- ✅ Email assíncrono (não bloqueia)
- ✅ Token JWT (stateless, sem consulta DB)

## 📋 Próximos Passos (Deploy)

### Para produção:
- [ ] **MFA/2FA**: Google Authenticator, SMS
- [ ] **Passkeys**: WebAuthn/FIDO2
- [ ] **CAPTCHA**: reCAPTCHA v3 ou hCaptcha
- [ ] **IP Whitelist**: Restringir IPs permitidos
- [ ] **Geolocation**: Alertar login de país diferente
- [ ] **Device Fingerprint**: Detectar dispositivos novos
- [ ] **HTTPS obrigatório**: Certificado SSL/TLS
- [ ] **WAF**: Web Application Firewall (CloudFlare, AWS WAF)

## 🧪 Testar Localmente

### 1. Tentativas falhas:
```bash
# Tente logar 5x com senha errada
# Verá: "Muitas tentativas falhas. Conta bloqueada por 5 minutos."
```

### 2. Senha fraca:
```python
# Ao criar usuário, senha deve ter:
# - 8+ caracteres
# - Maiúscula, minúscula, número, especial
```

### 3. Session timeout:
```bash
# Fique 15min inativo
# Token expira automaticamente
```

## 🔐 Configuração

### .env
```env
# Redis para cache de lockout
REDIS_HOST=redis_cache

# Email para notificações
ADMIN_NOTIFICATION_EMAILS=admin@empresa.com
```

## 📊 Monitoramento

### Admin Django:
- `/admin/notifications/loginlog/` - Ver todos os logins
- Filtrar por usuário, data, IP

### Logs:
```bash
docker-compose logs backend | grep "Login"
```

## 🛡️ Compliance

- ✅ **OWASP Top 10**: Protegido contra principais vulnerabilidades
- ✅ **LGPD**: Logs de acesso para auditoria
- ✅ **PCI-DSS**: Senhas hasheadas, sessões seguras
