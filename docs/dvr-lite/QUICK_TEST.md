# ⚡ Teste Rápido - Sprint 0

## 1️⃣ Subir Sistema (2 min)

```bash
cd d:\VMS
docker-compose up -d
```

Aguardar ~30s e verificar:
```bash
docker-compose ps
```

**Esperado:** Todos containers `healthy` ou `running` (exceto ai_detection e detection_consumer que foram removidos)

---

## 2️⃣ Testar API (1 min)

```bash
# Health check
curl http://localhost:8000/health
```

**Esperado:** `{"status": "ok"}`

---

## 3️⃣ Testar Frontend (1 min)

1. Abrir: http://localhost:5173
2. Fazer login (se tiver usuário criado)
3. Verificar que carrega sem erros

**Esperado:** 
- ✅ Página carrega
- ✅ Menu não mostra "Detecções"
- ✅ Console sem erros

---

## 4️⃣ Verificar Logs (1 min)

```bash
# Backend não deve ter erros
docker-compose logs backend --tail=20 | findstr /i "error"

# MediaMTX deve estar rodando
docker-compose logs mediamtx --tail=10
```

**Esperado:** Sem erros críticos

---

## ✅ Resultado

Se todos os testes passaram:
- ✅ Sistema funciona sem IA
- ✅ Streaming mantido
- ✅ Pronto para commit

---

## 🚀 Fazer Commit

```bash
git add .
git commit -m "chore: setup dvr-lite branch - remove AI detection services

- Remove ai_detection and detection_consumer from docker-compose
- Remove AI routes and logic from backend
- Remove DetectionsPage from frontend
- Update .env.example with DVR-focused variables
- Add governance and multi-tenant documentation
- Add technical specs for 50 cameras, 100 users, 1 VPS"

git push origin dvr-lite
```

---

## 📋 Atualizar Checklist

Marcar como concluído:
- [x] Testar que streaming ainda funciona
- [x] Commit: "chore: setup dvr-lite branch"
