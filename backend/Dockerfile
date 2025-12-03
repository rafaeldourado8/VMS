FROM python:3.11-slim

# Instalar dependências do sistema (Incluindo FFmpeg)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar e instalar dependências
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o código do projeto
COPY backend/ .

# Garantir que pastas existam
RUN mkdir -p /app/staticfiles /app/media /app/logs

EXPOSE 8000