FROM python:3.10-slim

WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Copia requirements
COPY requirements.txt .
# Instala dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia código
COPY . .
# Cria diretório para modelos
RUN mkdir -p models

# Expõe porta
EXPOSE 8002

# Comando para iniciar
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]