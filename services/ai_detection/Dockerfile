FROM python:3.10-slim

WORKDIR /app

# 1. Instala libs de sistema (CORRIGIDO: libgl1 no lugar de libgl1-mesa-glx)
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 2. Instala PyTorch CPU-Only (Leve)
RUN pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# 3. Copia e instala requirements
COPY requirements.sandbox.txt .
RUN pip install --no-cache-dir -r requirements.sandbox.txt

# 4. Copia o código
COPY . .

# 5. Executa o main
CMD ["python", "-u", "main.py"]