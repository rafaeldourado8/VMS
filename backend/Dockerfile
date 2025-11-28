# --- Estágio 1: Build do Frontend ---
FROM node:20-alpine AS frontend_builder
WORKDIR /frontend

# Removemos o corepack/pnpm e usamos npm nativo

# Copia package.json e package-lock.json (Em vez de pnpm-lock.yaml)
COPY frontend/package.json frontend/package-lock.json ./

# Instala dependências usando npm (npm ci é mais rápido e seguro para CI/CD/Docker)
RUN npm ci

# Copia o código fonte do frontend
COPY frontend/ ./

# Build do React/Vite usando npm
RUN npm run build

# --- Estágio 2: Build do Backend ---
FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 1. Dependências Python
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 2. Código Backend
COPY backend/ /app

# 3. Copia o build do frontend para o backend servir
# Como é um projeto Vite, a pasta de saída padrão é 'dist'
COPY --from=frontend_builder /frontend/dist /app/frontend_dist

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "120"]