# Configuração de Email Gmail para Notificações

## Passo a Passo - App Password do Gmail

### 1. Ativar Verificação em 2 Etapas
1. Acesse: https://myaccount.google.com/security
2. Clique em "Verificação em duas etapas"
3. Siga os passos para ativar

### 2. Gerar App Password
1. Acesse: https://myaccount.google.com/apppasswords
2. Selecione "App": **Outro (nome personalizado)**
3. Digite: **GT-Vision VMS**
4. Clique em "Gerar"
5. **COPIE A SENHA DE 16 DÍGITOS** (sem espaços)

### 3. Configurar no .env

```env
# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu.email@gmail.com
EMAIL_HOST_PASSWORD=xxxx xxxx xxxx xxxx  # App Password de 16 dígitos
DEFAULT_FROM_EMAIL=seu.email@gmail.com

# Emails que receberão notificações de login
ADMIN_NOTIFICATION_EMAILS=admin1@empresa.com,admin2@empresa.com
```

### 4. Testar no Django Shell

```bash
docker-compose exec backend python manage.py shell
```

```python
from django.core.mail import send_mail

send_mail(
    subject='Teste GT-Vision',
    message='Email funcionando!',
    from_email='seu.email@gmail.com',
    recipient_list=['destino@email.com'],
    fail_silently=False,
)
```

## Alternativa: Console Backend (Desenvolvimento)

Para desenvolvimento, use console (emails aparecem no terminal):

```env
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

## Alternativa: SMTP Próprio

Se tiver servidor SMTP próprio:

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.seudominio.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=noreply@seudominio.com
EMAIL_HOST_PASSWORD=sua_senha
DEFAULT_FROM_EMAIL=noreply@seudominio.com
ADMIN_NOTIFICATION_EMAILS=admin@seudominio.com
```

## Segurança

⚠️ **NUNCA commite o .env com credenciais reais!**

Adicione ao .gitignore:
```
.env
*.env
```

## Troubleshooting

### Erro: "Username and Password not accepted"
- Verifique se a verificação em 2 etapas está ativa
- Gere uma nova App Password
- Remova espaços da senha no .env

### Erro: "SMTPAuthenticationError"
- Confirme EMAIL_HOST_USER e EMAIL_HOST_PASSWORD
- Teste login manual no Gmail

### Emails não chegam
- Verifique spam/lixeira
- Confirme ADMIN_NOTIFICATION_EMAILS no .env
- Teste com console backend primeiro
