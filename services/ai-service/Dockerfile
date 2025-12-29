FROM python:3.11-slim

# Metadados
LABEL maintainer="GT-Vision Team"
LABEL description="GT-Vision AI Service - Unified LPR & Vehicle Detection"

WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia código da aplicação
COPY . .

# Cria diretórios necessários
RUN mkdir -p \
    /app/models \
    /app/logs \
    /app/captures \
    /app/pending_training \
    /app/received_webhooks

# Exposição de portas
EXPOSE 8000 9090

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Comando de inicialização
CMD ["python", "main.py"]
