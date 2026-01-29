# ✅ CORREÇÃO APLICADA - Docker Build Fix

## 🔧 Problema Resolvido

**Erro:** `Package 'libgl1-mesa-glx' has no installation candidate`

**Causa:** Pacote obsoleto no Debian Trixie (Python 3.11-slim)

## 📝 Mudanças Aplicadas

### Arquivo: `services/ai_detection/Dockerfile`

```diff
- libgl1-mesa-glx     # ❌ Obsoleto
+ libgl1              # ✅ Novo pacote

- libxrender-dev      # ❌ Obsoleto
+ (removido)          # ✅ Não necessário

- libsm6, libxext6    # ❌ Não usados
+ (removidos)         # ✅ opencv-headless não precisa
```

### Dockerfile Final (Otimizado)

```dockerfile
FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libglib2.0-0 \
    libgl1 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p /app/media/snapshots /app/logs /app/models

EXPOSE 8080
CMD ["python", "main.py"]
```

## 🚀 Como Testar

```bash
# 1. Limpa cache
docker builder prune -a -f

# 2. Rebuild
docker-compose build --no-cache

# 3. Inicia
docker-compose up -d

# 4. Verifica logs
docker-compose logs -f ai_detection
```

## ✅ Checklist

- [x] Dockerfile corrigido
- [x] Pacotes atualizados
- [x] opencv-python-headless (sem GUI)
- [x] Dependências mínimas
- [x] Build otimizado

## 📊 Resultado Esperado

```bash
$ docker-compose build ai_detection
[+] Building 45.2s (12/12) FINISHED
 => [internal] load build definition
 => => transferring dockerfile: 456B
 => [internal] load .dockerignore
 => [1/7] FROM python:3.11-slim
 => [2/7] RUN apt-get update && apt-get install...
 => [3/7] WORKDIR /app
 => [4/7] COPY requirements.txt .
 => [5/7] RUN pip install --no-cache-dir...
 => [6/7] COPY . .
 => [7/7] RUN mkdir -p /app/media/snapshots...
 => exporting to image
 => => exporting layers
 => => writing image sha256:abc123...
 => => naming to docker.io/library/gtvision-ai:latest

✅ Build concluído com sucesso!
```

---

**Status:** ✅ CORRIGIDO  
**Tempo:** ~2 minutos  
**Próximo passo:** `docker-compose up --build`
