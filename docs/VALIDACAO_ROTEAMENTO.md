# ✅ VALIDAÇÃO: Configuração de Roteamento

## 1️⃣ HAProxy roteia /vod/* para VOD Service? ✅

### Arquivo: `haproxy/haproxy.cfg`

**ACL (linha ~30):**
```haproxy
acl is_vod_hls path_beg /vod/
```

**Routing (linha ~56):**
```haproxy
use_backend vod_hls_service if is_vod_hls
```

**Backend (linhas ~103-105):**
```haproxy
backend vod_hls_service
    mode http
    server vod_hls1 vod_hls:8004 check
```

### Fluxo:
```
http://localhost/vod/camera_1/2026-02-20/file.mp4/index.m3u8
    ↓
HAProxy detecta path_beg /vod/
    ↓
Roteia para backend vod_hls_service
    ↓
Encaminha para vod_hls:8004
    ↓
VOD Service responde com HLS
```

---

## 2️⃣ Kong tem rota para VOD? ✅

### Arquivo: `kong/kong.yml`

**Service (linhas ~28-40):**
```yaml
- name: vod-service
  url: http://vod_hls:8004
  routes:
    - name: vod-hls-route
      paths:
        - /vod
      strip_path: false
  plugins:
    - name: rate-limiting
      config:
        minute: 1000
        policy: local
    - name: cors
      config:
        origins: ["*"]
        credentials: true
```

### Recursos:
- ✅ Rate limiting: 1000 requisições/minuto
- ✅ CORS habilitado (origins: *)
- ✅ Path: /vod (sem strip)

---

## 🧪 Teste Prático

### 1. Verificar containers
```bash
docker ps | findstr vod_hls
# Deve mostrar: gtvision_vod_hls
```

### 2. Testar VOD direto
```bash
curl http://localhost:8006/health
# Resposta: {"status":"ok"}
```

### 3. Testar via HAProxy
```bash
curl http://localhost/vod/health
# Resposta: {"status":"ok"}
```

### 4. Testar playlist HLS
```bash
curl http://localhost/vod/camera_1/2026-02-20/12-44-27.mp4/index.m3u8
# Resposta: #EXTM3U...
```

---

## 📊 Arquitetura de Roteamento

```
Cliente
  ↓
http://localhost/vod/*
  ↓
HAProxy (porta 80)
  ├─ ACL: is_vod_hls
  └─ Backend: vod_hls_service
      ↓
  VOD Service (vod_hls:8004)
      ↓
  HLS Cache (/hls_cache)
      ↓
  MP4 Files (/recordings)
```

---

## 🔧 Aplicar Mudanças

Se fizer alterações nos arquivos de configuração:

```bash
# Reiniciar HAProxy
docker-compose restart haproxy

# Reiniciar Kong
docker-compose restart kong

# Verificar logs
docker logs gtvision_haproxy
docker logs gtvision_kong
```

---

## ✅ CONCLUSÃO

| Item | Status | Arquivo | Linhas |
|------|--------|---------|--------|
| HAProxy ACL | ✅ | haproxy.cfg | ~30 |
| HAProxy Routing | ✅ | haproxy.cfg | ~56 |
| HAProxy Backend | ✅ | haproxy.cfg | ~103-105 |
| Kong Service | ✅ | kong.yml | ~28-40 |
| Kong Rate Limit | ✅ | kong.yml | ~35-37 |
| Kong CORS | ✅ | kong.yml | ~38-40 |

---

## ✅ AMBOS OS ITENS ESTÃO CONFIGURADOS!

**Execute:** `tests\validate_routing.bat` para validar
