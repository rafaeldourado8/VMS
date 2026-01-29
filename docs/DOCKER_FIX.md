# 🔧 FIX: Erro libgl1-mesa-glx no Docker Build

## ❌ Problema
```
Package 'libgl1-mesa-glx' has no installation candidate
```

## ✅ Solução Aplicada

O pacote `libgl1-mesa-glx` foi **obsoleto** no Debian Trixie (usado pelo Python 3.11-slim).

### Mudanças no Dockerfile:

**ANTES (❌ Erro):**
```dockerfile
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libgl1-mesa-glx \      # ❌ Obsoleto
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \       # ❌ Obsoleto
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*
```

**DEPOIS (✅ Corrigido):**
```dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libglib2.0-0 \
    libgl1 \               # ✅ Novo pacote
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*
```

## 📦 Pacotes Removidos (Desnecessários)

- `libsm6` - Não usado pelo OpenCV headless
- `libxext6` - Não usado sem GUI
- `libxrender-dev` → `libxrender1` (mas removido, não necessário)

## 🚀 Como Rebuildar

```bash
# Limpa cache do Docker
docker builder prune -a -f

# Rebuild
docker-compose build --no-cache ai_detection

# Ou rebuild tudo
docker-compose build --no-cache
```

## 🧪 Testar Build

```bash
cd services/ai_detection
docker build -t test-ai .

# Se funcionar:
docker run --rm test-ai python -c "import cv2; print('✅ OpenCV OK')"
```

## 📝 Alternativa: Usar Debian Bookworm

Se ainda tiver problemas, use uma versão mais antiga do Python:

```dockerfile
FROM python:3.11-bookworm  # Em vez de slim

RUN apt-get update && apt-get install -y \
    ffmpeg \
    libgl1-mesa-glx \  # Funciona no Bookworm
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*
```

## ✅ Status

- ✅ Dockerfile corrigido
- ✅ Pacotes atualizados para Debian Trixie
- ✅ Build deve funcionar agora

**Tente novamente:**
```bash
docker-compose up --build
```
