FROM python:3.10-slim

WORKDIR /app

# Instala dependências do sistema + git
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libgl1 libglib2.0-0 git \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Instala dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Cria diretórios necessários
RUN mkdir -p /app/models /app/detections

# Healthcheck simples
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s \
    CMD python -c "import sys; sys.exit(0)"

CMD ["python", "main.py"]