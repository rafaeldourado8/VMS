# Certificados SSL para HAProxy

## Desenvolvimento (Self-Signed)

```bash
openssl req -x509 -newkey rsa:4096 -nodes -keyout haproxy/certs/key.pem -out haproxy/certs/cert.pem -days 365 -subj "/CN=localhost"
cat haproxy/certs/cert.pem haproxy/certs/key.pem > haproxy/certs/cert.pem
```

## Produção (Let's Encrypt)

```bash
certbot certonly --standalone -d seu-dominio.com
cat /etc/letsencrypt/live/seu-dominio.com/fullchain.pem /etc/letsencrypt/live/seu-dominio.com/privkey.pem > haproxy/certs/cert.pem
```

## Desabilitar HTTPS (Dev)

Comente no `haproxy.cfg`:
- `bind *:443 ssl ...`
- `http-request redirect scheme https ...`
- `http-response set-header Strict-Transport-Security ...`
