FROM python:3.11-slim

WORKDIR /app

# Instala FFmpeg e dependências
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copia requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia código
COPY . .

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1
ENV RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/
ENV REDIS_URL=redis://redis_ai:6379/3
ENV DB_URL=postgresql://ai_user:ai_pass@postgres_ai/ai_detections

CMD ["python", "main.py"]