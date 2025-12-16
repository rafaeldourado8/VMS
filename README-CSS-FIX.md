# 🎨 Correção Rápida - CSS do Django

## 🚨 Problema
Django Admin sem CSS (aparece sem formatação).

## ✅ Solução em 3 Passos

### 1️⃣ Execute o script de correção
```bash
fix-css.bat
```

### 2️⃣ Aguarde a conclusão (30 segundos)

### 3️⃣ Limpe o cache do navegador
- Pressione **Ctrl+F5** no navegador
- Ou **Ctrl+Shift+Delete** → Limpar cache

---

## 📋 Scripts Disponíveis

### `fix-css.bat` - Corrige o problema
- Coleta arquivos estáticos
- Verifica volumes
- Reinicia serviços
- **Use este quando o CSS não aparecer**

### `check-static.bat` - Diagnóstico
- Verifica se arquivos existem
- Testa acesso HTTP
- Mostra status dos containers
- **Use este para diagnosticar o problema**

### `fix-services.bat` - Correção completa
- Reinicia todos os serviços
- Limpa volumes problemáticos
- Reconstrói containers
- **Use este para problemas mais graves**

---

## 🔍 Verificação Rápida

Após executar `fix-css.bat`, verifique:

1. **Admin Django:** http://localhost/admin/
   - Deve aparecer com CSS azul do Django

2. **API Docs:** http://localhost/api/docs/
   - Deve aparecer com interface Swagger

3. **Console do navegador (F12):**
   - Não deve ter erros 404 em arquivos CSS

---

## 🐛 Ainda não funciona?

1. Execute o diagnóstico:
```bash
check-static.bat
```

2. Veja o guia completo:
```bash
TROUBLESHOOTING-CSS.md
```

3. Reconstrua tudo:
```bash
docker-compose down -v
docker-compose up -d --build
fix-css.bat
```

---

## 💡 Dica

Sempre que fizer mudanças no Django, execute:
```bash
docker-compose exec backend python manage.py collectstatic --noinput
docker-compose restart nginx
```

---

**Desenvolvido por Rafael Dourado**
