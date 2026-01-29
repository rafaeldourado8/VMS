FROM python:3.10-slim

WORKDIR /app

# Set headless mode for OpenCV
ENV QT_QPA_PLATFORM=offscreen
ENV OPENCV_VIDEOIO_DEBUG=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt easyocr

# Copy application
COPY . .

CMD ["uvicorn", "lpr_manager:app", "--host", "0.0.0.0", "--port", "8080"]
