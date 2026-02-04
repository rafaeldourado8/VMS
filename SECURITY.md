# 🔒 Guia de Segurança para Produção

## ⚠️ CRÍTICO - Antes de Subir para VPS

### 1. HTTPS/SSL (Obrigatório)

**Problema:** Tráfego HTTP não criptografado expõe senhas e dados.

**Solução:**

```bash
# Para desenvolvimento (certificado autoassinado):
bash generate-ssl.sh

# Para produção (Let's Encrypt - RECOMENDADO):
# 1. Instale certbot no servidor
sudo apt install certbot

# 2. Gere certificado (substitua seudominio.com):
sudo certbot certonly --standalone -d seudominio.com -d www.seudominio.com

# 3. Copie certificados para o HAProxy:
sudo cat /etc/letsencrypt/live/seudominio.com/fullchain.pem \
         /etc/letsencrypt/live/seudominio.com/privkey.pem \
         > haproxy/certs/cert.pem

# 4. Use haproxy.prod.cfg no docker-compose.yml
```

### 2. Remover Regras de Desenvolvimento

**Problema:** Vite exposto permite acesso ao código-fonte.

**Solução:**

```yaml
# No docker-compose.yml, REMOVA ou COMENTE:
# frontend:
#   image: node:20-slim
#   ...

# Use haproxy.prod.cfg que não tem regras do Vite
```

### 3. Configurar CORS Correto

**Problema:** Kong bloqueará requisições do domínio real.

**Solução:**

```bash
# No arquivo .env:
CORS_ORIGIN=https://seudominio.com

# Reinicie o Kong:
docker-compose restart kong
```

### 4. Proteger Página de Stats

**Problema:** Estatísticas expostas sem senha.

**Solução:**

```bash
# No arquivo .env:
HAPROXY_STATS_PASSWORD=senha_muito_forte_aqui

# Stats agora só acessível via localhost:8404
# Para acessar remotamente, use SSH tunnel:
ssh -L 8404:localhost:8404 usuario@seu-servidor
# Depois acesse: http://localhost:8404/stats
```

### 5. Variáveis de Ambiente Seguras

**Problema:** Senhas padrão são inseguras.

**Solução:**

```bash
# Copie o exemplo:
cp .env.production.example .env

# Edite e coloque senhas fortes:
nano .env

# Gere senhas fortes:
openssl rand -base64 32
```

### 6. Build do Frontend para Produção

**Problema:** Vite dev server não deve ser usado em produção.

**Solução:**

```bash
# 1. Build do frontend:
cd frontend
npm run build

# 2. Configure Nginx para servir os arquivos estáticos:
# Veja nginx/nginx.prod.conf

# 3. Remova o container frontend do docker-compose.yml
```

## 📋 Checklist de Segurança

- [ ] Certificado SSL configurado (Let's Encrypt)
- [ ] HAProxy usando haproxy.prod.cfg
- [ ] CORS_ORIGIN configurado com domínio real
- [ ] HAPROXY_STATS_PASSWORD definido
- [ ] Todas as senhas alteradas no .env
- [ ] DEBUG=False no Django
- [ ] Frontend buildado (npm run build)
- [ ] Container Vite removido do docker-compose
- [ ] Firewall configurado (apenas 80, 443, 22)
- [ ] Backup automático do banco de dados

## 🚀 Deploy Seguro

```bash
# 1. No servidor VPS:
git clone seu-repositorio
cd VMS

# 2. Configure variáveis:
cp .env.production.example .env
nano .env  # Edite com senhas fortes

# 3. Gere certificado SSL:
sudo certbot certonly --standalone -d seudominio.com

# 4. Copie certificado:
sudo cat /etc/letsencrypt/live/seudominio.com/fullchain.pem \
         /etc/letsencrypt/live/seudominio.com/privkey.pem \
         > haproxy/certs/cert.pem

# 5. Use configuração de produção:
# Edite docker-compose.yml e troque haproxy.cfg por haproxy.prod.cfg

# 6. Suba os containers:
docker-compose up -d

# 7. Verifique:
docker-compose ps
curl -I https://seudominio.com
```

## 🔄 Renovação Automática SSL

```bash
# Adicione ao crontab:
sudo crontab -e

# Adicione esta linha (renova a cada 2 meses):
0 0 1 */2 * certbot renew --quiet && cat /etc/letsencrypt/live/seudominio.com/fullchain.pem /etc/letsencrypt/live/seudominio.com/privkey.pem > /caminho/para/VMS/haproxy/certs/cert.pem && docker-compose -f /caminho/para/VMS/docker-compose.yml restart haproxy
```
