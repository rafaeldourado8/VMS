# 🧪 Guia de Testes - DVR-Lite Sprint 0

## Pré-requisitos
- Docker e Docker Compose instalados
- Branch `dvr-lite` ativa
- Portas 80, 8000, 8888, 5432, 6379 disponíveis

---

## 1️⃣ Teste de Inicialização

### Subir os serviços
```bash
cd d:\VMS
docker-compose up -d
```

### Verificar status dos containers
```bash
docker-compose ps
```

**Resultado esperado:**
```
✅ gtvision_backend       - healthy
✅ gtvision_postgres      - healthy
✅ gtvision_redis         - healthy
✅ gtvision_rabbitmq      - healthy
✅ gtvision_mediamtx      - healthy
✅ gtvision_streaming     - healthy
✅ gtvision_frontend      - running
✅ gtvision_haproxy       - running
✅ gtvision_kong          - healthy
✅ gtvision_prometheus    - healthy

❌ NÃO DEVE EXISTIR:
   - gtvision_ai_detection
   - gtvision_detection_consumer
```

### Verificar logs
```bash
# Backend deve subir sem erros
docker-compose logs backend | grep -i error

# MediaMTX deve estar pronto
docker-compose logs mediamtx | grep -i "listener opened"

# Frontend deve compilar
docker-compose logs frontend | grep -i "ready"
```

---

## 2️⃣ Teste de API

### Health Check
```bash
curl http://localhost:8000/health
```
**Esperado:** `{"status": "ok"}`

### Login
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "admin123"
  }'
```
**Esperado:** Token JWT

### Listar Câmeras (com token)
```bash
TOKEN="seu_token_aqui"
curl http://localhost:8000/api/cameras/ \
  -H "Authorization: Bearer $TOKEN"
```
**Esperado:** Lista de câmeras (pode estar vazia)

### Verificar que rotas de IA foram removidas
```bash
# Deve retornar 404
curl -X POST http://localhost:8000/api/ai/cameras/1/start/ \
  -H "Authorization: Bearer $TOKEN"

# Deve retornar 404
curl http://localhost:8000/api/detections/
```

---

## 3️⃣ Teste de Frontend

### Acessar aplicação
1. Abrir navegador: http://localhost:5173
2. Fazer login com credenciais de teste
3. Verificar que carrega sem erros de console

### Verificar menu de navegação
**Deve conter:**
- ✅ Dashboard
- ✅ Câmeras
- ✅ Meus Clips
- ✅ Mosaicos
- ✅ Configurações

**NÃO deve conter:**
- ❌ Detecções

### Verificar páginas
1. **Dashboard:** Deve carregar sem erros
2. **Câmeras:** Deve mostrar lista (vazia ou com câmeras)
3. **Clips:** Deve carregar (vazio por enquanto)
4. **Mosaicos:** Deve carregar
5. **Configurações:** Deve carregar

### Console do navegador
Abrir DevTools (F12) e verificar:
- ❌ Sem erros de import
- ❌ Sem erros de rotas não encontradas
- ❌ Sem warnings de componentes faltando

---

## 4️⃣ Teste de Streaming

### Adicionar câmera de teste
```bash
TOKEN="seu_token_aqui"

curl -X POST http://localhost:8000/api/cameras/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Câmera Teste",
    "stream_url": "rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mp4",
    "location": "Teste"
  }'
```

### Verificar stream no MediaMTX
```bash
# Listar paths ativos
curl -u mediamtx_api_user:GtV\!sionMed1aMTX\$2025 \
  http://localhost:9997/v3/paths/list
```

### Testar HLS no navegador
1. Ir para página de Câmeras
2. Câmera deve aparecer na lista
3. Stream deve carregar (pode demorar 10s)
4. Thumbnail deve ser gerado após 10s

### Verificar thumbnail
```bash
curl http://localhost:8001/api/cameras/1/thumbnail
```
**Esperado:** Imagem JPEG

---

## 5️⃣ Teste de Banco de Dados

### Conectar ao PostgreSQL
```bash
docker exec -it gtvision_postgres psql -U vms -d vms_mvp
```

### Verificar tabelas
```sql
-- Listar tabelas
\dt

-- Verificar câmeras
SELECT id, name, stream_url FROM cameras_camera;

-- Verificar que não há detecções (tabela pode não existir)
SELECT COUNT(*) FROM deteccoes_deteccao;
```

---

## 6️⃣ Teste de Redis

### Conectar ao Redis
```bash
docker exec -it gtvision_redis redis-cli
```

### Verificar cache
```redis
# Listar todas as keys
KEYS *

# Verificar cache de thumbnails
KEYS thumbnail:*

# Verificar sessões
KEYS session:*
```

---

## 7️⃣ Teste de Prometheus

### Acessar Prometheus
http://localhost:9090

### Verificar targets
1. Status → Targets
2. Verificar que todos os endpoints estão UP

### Testar query
```promql
up{job="backend"}
```
**Esperado:** Valor 1

---

## 8️⃣ Teste de Performance

### Adicionar múltiplas câmeras
```bash
# Script para adicionar 10 câmeras
for i in {1..10}; do
  curl -X POST http://localhost:8000/api/cameras/ \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
      \"name\": \"Câmera $i\",
      \"stream_url\": \"rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mp4\",
      \"location\": \"Teste $i\"
    }"
done
```

### Verificar paginação
1. Ir para página de Câmeras
2. Deve mostrar 10 câmeras por página
3. Lazy loading deve funcionar ao rolar

### Verificar uso de recursos
```bash
# CPU e memória dos containers
docker stats --no-stream

# Uso de disco
docker system df
```

---

## 9️⃣ Teste de Limpeza

### Remover câmera
```bash
curl -X DELETE http://localhost:8000/api/cameras/1/ \
  -H "Authorization: Bearer $TOKEN"
```

### Verificar que foi removida
```bash
curl http://localhost:8000/api/cameras/ \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🔟 Teste de Logs

### Verificar logs de todos os serviços
```bash
# Backend
docker-compose logs backend --tail=50

# MediaMTX
docker-compose logs mediamtx --tail=50

# Streaming
docker-compose logs streaming --tail=50

# Frontend
docker-compose logs frontend --tail=50
```

**Verificar:**
- ❌ Sem erros críticos
- ❌ Sem stack traces
- ❌ Sem menções a "ai_detection" ou "lpr_detection"

---

## ✅ Checklist Final

Antes de fazer commit, verificar:

- [ ] Todos os containers sobem sem erros
- [ ] API responde corretamente
- [ ] Frontend carrega sem erros
- [ ] Menu não mostra "Detecções"
- [ ] Streaming funciona
- [ ] Thumbnails são gerados
- [ ] Paginação funciona
- [ ] Não há serviços de IA rodando
- [ ] Logs estão limpos
- [ ] Prometheus coleta métricas

---

## 🐛 Troubleshooting

### Container não sobe
```bash
# Ver logs detalhados
docker-compose logs [service_name]

# Rebuild
docker-compose build [service_name]
docker-compose up -d [service_name]
```

### Frontend com erro de import
```bash
# Limpar node_modules
docker-compose exec frontend rm -rf node_modules
docker-compose restart frontend
```

### MediaMTX não aceita streams
```bash
# Verificar configuração
docker exec gtvision_mediamtx cat /mediamtx.yml

# Restart
docker-compose restart mediamtx
```

### Banco de dados com erro
```bash
# Verificar conexão
docker exec gtvision_postgres pg_isready -U vms

# Ver logs
docker-compose logs postgres_db
```

---

## 📝 Relatório de Testes

Após executar todos os testes, preencher:

```
Data: ___/___/___
Testador: ___________

✅ Inicialização: [ ] OK [ ] FALHOU
✅ API: [ ] OK [ ] FALHOU
✅ Frontend: [ ] OK [ ] FALHOU
✅ Streaming: [ ] OK [ ] FALHOU
✅ Banco de Dados: [ ] OK [ ] FALHOU
✅ Redis: [ ] OK [ ] FALHOU
✅ Prometheus: [ ] OK [ ] FALHOU
✅ Performance: [ ] OK [ ] FALHOU
✅ Limpeza: [ ] OK [ ] FALHOU
✅ Logs: [ ] OK [ ] FALHOU

Observações:
_________________________________
_________________________________
_________________________________

Pronto para commit? [ ] SIM [ ] NÃO
```

---

## 🎯 Próximo Passo

Se todos os testes passaram:
```bash
git add .
git commit -m "chore: setup dvr-lite branch - remove AI detection services"
git push origin dvr-lite
```

Depois, marcar no checklist:
- [x] Testar que streaming ainda funciona
- [x] Commit: "chore: setup dvr-lite branch"
