# VMS/backend/Dockerfile (Corrigido)

# --- Estágio 1: Build do Frontend ---
# (Esta parte está correta e permanece igual)
FROM node:18-alpine AS frontend_builder
WORKDIR /frontend
COPY ../frontend/package*.json ./
RUN npm ci --prefer-offline --no-audit --no-fund
COPY ../frontend ./
RUN npm run build

# --- Estágio 2: Build do Backend ---
FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 1. Copie o requirements.txt primeiro
COPY ./backend/requirements.txt /app/requirements.txt
# 2. Instale as dependências
RUN pip install --no-cache-dir -r requirements.txt

# 3. Copie o código do backend (incluindo o settings.py corrigido)
COPY ./backend /app

# 4. AGORA copie os ficheiros do frontend construídos
#    (Isto garante que não é sobreposto pelo passo 3)
COPY --from=frontend_builder /frontend/dist /app/frontend_dist

# 5. Finalmente, corra o collectstatic
#    (Agora o Django vai encontrar /app/frontend_dist)

# Expõe a porta do Django
EXPOSE 8000

# Comando padrão para rodar o servidor
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "120"]