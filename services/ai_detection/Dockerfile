FROM python:3.11-slim

WORKDIR /app

# Instala FFmpeg e dependências
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copia requirements e instala
COPY requirements.txt .
RUN pip install --no-cache-dir torch==2.1.0+cpu torchvision==0.16.0+cpu --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir -r requirements.txt

# Copia código
COPY . .

# Copia modelo YOLO
COPY yolov8n.pt /app/yolov8n.pt

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1
ENV RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/
ENV REDIS_URL=redis://redis_ai:6379/3
ENV DB_URL=postgresql://ai_user:ai_pass@postgres_ai/ai_detections

CMD ["python", "main.py"]