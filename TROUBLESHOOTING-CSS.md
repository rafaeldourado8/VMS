# 🎨 Troubleshooting - CSS do Django Admin

## Problema
O Django Admin está sem CSS (aparece sem formatação, apenas HTML puro).

## Causa
Os arquivos estáticos não foram coletados ou não estão sendo servidos corretamente pelo Nginx.

---

## ✅ Solução Rápida

### Opção 1: Script Automático (RECOMENDADO)
```bash
fix-css.bat
```

### Opção 2: Manual
```bash
# 1. Coletar arquivos estáticos
docker-compose exec backend python manage.py collectstatic --noinput --clear

# 2. Verificar se foram coletados
docker-compose exec backend ls -la /app/staticfiles/admin/css/

# 3. Verificar se Nginx tem acesso
docker-compose exec nginx ls -la /var/www/static/admin/css/

# 4. Reiniciar serviços
docker-compose restart backend nginx

# 5. Limpar cache do navegador (Ctrl+F5)
```

---

## 🔍 Diagnóstico

### Verificar se collectstatic rodou
```bash
docker-compose logs backend | grep collectstatic
```

**Esperado:** Deve mostrar mensagens como "X static files copied"

### Verificar volume compartilhado
```bash
docker volume inspect vms_backend_static
```

### Verificar configuração do Nginx
```bash
docker-compose exec nginx cat /etc/nginx/nginx.conf | grep static
```

**Esperado:**
```nginx
location /static/ {
    alias /var/www/static/;
    expires 7d;
}
```

### Testar acesso direto ao CSS
```bash
curl -I http://localhost/static/admin/css/base.css
```

**Esperado:** HTTP 200 OK

---

## 🐛 Problemas Comuns

### 1. Volume não montado corretamente
**Sintoma:** Nginx não encontra os arquivos

**Solução:**
```bash
docker-compose down
docker volume rm vms_backend_static
docker-compose up -d
docker-compose exec backend python manage.py collectstatic --noinput
```

### 2. Permissões incorretas
**Sintoma:** Erro 403 Forbidden

**Solução:**
```bash
docker-compose exec backend chmod -R 755 /app/staticfiles
docker-compose restart nginx
```

### 3. Cache do navegador
**Sintoma:** CSS ainda não aparece após correção

**Solução:**
- Chrome/Edge: Ctrl+Shift+Delete → Limpar cache
- Firefox: Ctrl+Shift+Delete → Limpar cache
- Ou simplesmente: Ctrl+F5 (hard refresh)

### 4. WhiteNoise conflitando
**Sintoma:** CSS funciona no backend mas não no Nginx

**Solução:** Verificar `settings.py`:
```python
# Deve estar assim:
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
```

---

## 📊 Verificação Final

Após aplicar a correção, verifique:

- [ ] Admin Django carrega com CSS: http://localhost/admin/
- [ ] API Docs carrega corretamente: http://localhost/api/docs/
- [ ] Arquivos estáticos acessíveis: http://localhost/static/admin/css/base.css
- [ ] Sem erros 404 no console do navegador (F12)

---

## 🆘 Ainda não funciona?

1. **Verifique os logs:**
```bash
docker-compose logs backend | tail -50
docker-compose logs nginx | tail -50
```

2. **Reconstrua os containers:**
```bash
docker-compose down
docker-compose up -d --build
```

3. **Verifique o HAProxy:**
```bash
# HAProxy pode estar bloqueando
curl -I http://localhost:80/static/admin/css/base.css
```

4. **Teste direto no backend (bypass Nginx):**
```bash
docker-compose exec backend python manage.py runserver 0.0.0.0:9000
# Acesse: http://localhost:9000/admin/
```

---

## 📝 Configuração Correta

### settings.py
```python
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # Logo após SecurityMiddleware
    # ... outros middlewares
]
```

### docker-compose.yml
```yaml
backend:
  volumes:
    - backend_static:/app/staticfiles

nginx:
  volumes:
    - backend_static:/var/www/static:ro

volumes:
  backend_static:
```

### nginx.simple.conf
```nginx
location /static/ {
    alias /var/www/static/;
    expires 7d;
    access_log off;
}
```

---

## ✅ Prevenção

Para evitar este problema no futuro:

1. **Sempre rode collectstatic após mudanças:**
```bash
docker-compose exec backend python manage.py collectstatic --noinput
```

2. **Adicione ao entrypoint.sh:**
```bash
python manage.py collectstatic --noinput
```

3. **Verifique antes de commit:**
```bash
git add .
docker-compose exec backend python manage.py collectstatic --noinput
git commit -m "feat: nova funcionalidade"
```

---

**Desenvolvido por Rafael Dourado**
