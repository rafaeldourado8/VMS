FROM python:3.11-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    ffmpeg \
    tesseract-ocr \
    tesseract-ocr-eng \
    && rm -rf /var/lib/apt/lists/*

# Install PyTorch CPU-only first
RUN pip install --no-cache-dir torch==2.1.0 torchvision==0.16.0 --index-url https://download.pytorch.org/whl/cpu

# Install other dependencies
RUN pip install --no-cache-dir \
    opencv-python-headless==4.8.1.78 \
    numpy==1.24.3 \
    requests==2.31.0 \
    python-dotenv==1.0.0 \
    pytesseract==0.3.10 \
    Pillow==10.0.0 \
    imutils==0.5.4 \
    scikit-image==0.21.0 \
    ultralytics==8.0.196

# Copy code
COPY . .

# Create directories
RUN mkdir -p models media/detections

CMD ["python", "main.py"]
