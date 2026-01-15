# 🐳 Docker Setup for ALPR YOLOv8

## Quick Start

### 1. Prepare Models

```bash
cd ai/resources

# Combine split files
cat yolov8n_* > yolov8n.pt
cat tdiblik_lp_finetuned_yolov8n_* > tdiblik_lp_finetuned_yolov8n.pt
```

### 2. Configure Environment

```bash
# Create .env file
echo "RTSP_URL=rtsp://username:password@ip:554/stream" > .env
```

### 3. Run with Docker Compose

```bash
docker-compose up -d
```

### 4. View Logs

```bash
docker-compose logs -f alpr-server
```

## Manual Docker Build

```bash
# Build
docker build -t alpr-yolov8:latest .

# Run
docker run -d \
  --name alpr-server \
  -p 8765:8765 \
  -v $(pwd)/server/results:/app/server/results \
  -v $(pwd)/ai/resources:/app/ai/resources:ro \
  -e RTSP_CAPTURE_CONFIG="rtsp://..." \
  alpr-yolov8:latest
```

## Configuration

All environment variables from `.env.development` are supported:

- `DEBUG`: Enable debug mode
- `WS_PORT`: WebSocket port (default: 8765)
- `RTSP_CAPTURE_CONFIG`: RTSP URL or video file path
- `PURE_YOLO_MODEL_PATH`: Vehicle detection model
- `LICENSE_PLATE_YOLO_MODEL_PATH`: Plate detection model
- `SAVE_RESULTS_ENABLED`: Save detection images
- `RESULTS_PATH`: Output directory for results
- `SKIP_BEFORE_Y_MAX`: Distance threshold

## Results

Detection results are saved in `server/results/`:
- `{uuid}_car.jpg`: Vehicle image
- `{uuid}_lp.jpg`: License plate image

## WebSocket Client

Connect to `ws://localhost:8765` to receive real-time detections.

## Troubleshooting

### Models not found
```bash
# Verify models exist
ls -la ai/resources/*.pt
```

### RTSP connection failed
```bash
# Test RTSP URL
ffmpeg -i "rtsp://..." -frames:v 1 test.jpg
```

### Tesseract not working
```bash
# Inside container
docker exec -it alpr-server tesseract --version
```
