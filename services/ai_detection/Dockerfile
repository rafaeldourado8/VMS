FROM python:3.10-slim

WORKDIR /app

# 1. Instala libs de sistema
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 2. Instala PyTorch CPU-Only
RUN pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# 3. Copia e instala requirements
COPY requirements.sandbox.txt .
RUN pip install --no-cache-dir -r requirements.sandbox.txt

# 4. Copia fast-plate-ocr e pre-download modelo
COPY fast-plate-ocr-master /app/fast-plate-ocr-master
RUN python -c "import sys; sys.path.append('/app/fast-plate-ocr-master'); from fast_plate_ocr.inference.plate_recognizer import LicensePlateRecognizer; LicensePlateRecognizer(hub_ocr_model='cct-xs-v1-global-model')" || echo "OCR model download failed, will retry at runtime"

# 5. Copia o resto do código
COPY . .

# 6. Executa o main
CMD ["python", "-u", "main.py"]