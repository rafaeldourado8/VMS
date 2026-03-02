# Frontend Connection Refused - Solução

## 🔴 Problema

O HAProxy reporta erro recorrente:
```
Server frontend_dev/frontend1 is DOWN, reason: Layer4 connection problem, info: "Connection refused"
backend 'frontend_dev' has no server available!
```

## 🔍 Causa Raiz

1. **Vite demora para iniciar** - O npm install e inicialização do Vite podem levar 30-60s
2. **Hot reload reinicia o servidor** - Mudanças no código fazem o Vite reiniciar
3. **HAProxy muito agressivo** - Marca o backend como DOWN rapidamente
4. **Sem healthcheck no container** - Docker não sabe se o frontend está realmente pronto

## ✅ Soluções Implementadas

### 1. Healthcheck no Docker Compose
```yaml
healthcheck:
  test: ["CMD-SHELL", "wget -q --spider http://localhost:5173 || exit 1"]
  interval: 10s
  timeout: 5s
  retries: 5
  start_period: 60s  # Dá tempo para npm install
```

### 2. HAProxy Mais Tolerante
```haproxy
backend frontend_dev
    # Aceita mais status codes
    http-check expect status 200,403,404
    
    # Timeouts maiores
    timeout server 120s
    timeout connect 30s
    
    # Retry mais agressivo
    default-server inter 5s fastinter 2s downinter 3s rise 2 fall 3
```

**Parâmetros:**
- `inter 5s` - Verifica a cada 5s (padrão era 10s)
- `fastinter 2s` - Verifica a cada 2s quando em transição
- `downinter 3s` - Verifica a cada 3s quando DOWN
- `rise 2` - 2 checks OK para marcar como UP
- `fall 3` - 3 checks falhos para marcar como DOWN (era 5)

### 3. Scripts de Monitoramento

**Windows:**
```bash
scripts\monitor_frontend.bat
```

**Linux/Mac:**
```bash
bash scripts/monitor_frontend.sh
```

Monitora o frontend a cada 15s e reinicia automaticamente se detectar falha.

## 🚀 Como Aplicar

### Opção 1: Recriar o Container (Recomendado)
```bash
docker-compose down frontend
docker-compose up -d frontend
```

### Opção 2: Restart Completo
```bash
docker-compose restart haproxy frontend
```

### Opção 3: Usar Monitor Automático
```bash
# Windows
start scripts\monitor_frontend.bat

# Linux/Mac
bash scripts/monitor_frontend.sh &
```

## 📊 Verificar Status

### Ver logs do HAProxy
```bash
docker logs -f gtvision_haproxy
```

### Ver logs do Frontend
```bash
docker logs -f gtvision_frontend
```

### Verificar health do frontend
```bash
docker inspect gtvision_frontend | grep -A 10 Health
```

### Stats do HAProxy
Acesse: http://localhost:8404/stats

## 🔧 Troubleshooting

### Frontend ainda cai?

1. **Aumentar memória do container:**
```yaml
frontend:
  deploy:
    resources:
      limits:
        memory: 2G
```

2. **Desabilitar HMR (Hot Module Reload):**
```bash
# No package.json, adicionar flag --no-hmr
"dev": "vite --host 0.0.0.0 --port 5173 --no-hmr"
```

3. **Usar build de produção:**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### HAProxy marca como DOWN mesmo com frontend OK?

Verifique se há firewall/antivírus bloqueando:
```bash
# Teste direto
curl http://localhost:5173

# Teste do container do HAProxy
docker exec gtvision_haproxy wget -q -O- http://frontend:5173
```

## 📈 Melhorias Futuras

1. **Nginx como proxy reverso para o Vite** - Mais estável que acesso direto
2. **Build de produção** - Servir arquivos estáticos ao invés do dev server
3. **CDN/Cache** - Reduzir carga no frontend
4. **Load balancer** - Múltiplas instâncias do frontend

## 🎯 Resultado Esperado

Após aplicar as soluções:
- ✅ Frontend inicia em ~60s
- ✅ HAProxy aguarda até 60s antes de marcar como DOWN
- ✅ Reinícios automáticos em caso de falha
- ✅ Menos interrupções durante desenvolvimento
