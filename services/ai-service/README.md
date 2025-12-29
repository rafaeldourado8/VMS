# GT-Vision AI Service v2.0

**Unified AI Service with LPR, Motion Detection and Dual-Mode Processing**

---

## 🚀 Features

### Core Capabilities
- ✅ **YOLO Vehicle Detection** (cars, motorcycles, buses, trucks)
- ✅ **License Plate Recognition (LPR)** using `fast-plate-ocr`
- ✅ **Motion Detection** for CPU/GPU optimization
- ✅ **Dual-Mode Processing**: Task Queue + RTSP Streams
- ✅ **Webhook Support** for external LPR cameras
- ✅ **Prometheus Metrics** for monitoring
- ✅ **Auto-training Data Collection**

### Architecture
```
┌─────────────────────────────────────────────────┐
│              GT-Vision AI Service               │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌──────────────┐      ┌──────────────┐       │
│  │ Task Workers │      │Stream Workers│       │
│  │  (Redis Q)   │      │ (RTSP+Motion)│       │
│  └──────────────┘      └──────────────┘       │
│                                                 │
│  ┌──────────────────────────────────┐         │
│  │     Vehicle Detector (YOLO)      │         │
│  └──────────────────────────────────┘         │
│                                                 │
│  ┌──────────────────────────────────┐         │
│  │   LPR (fast-plate-ocr)           │         │
│  └──────────────────────────────────┘         │
│                                                 │
│  ┌──────────────────────────────────┐         │
│  │   Motion Detector (MOG2)         │         │
│  └──────────────────────────────────┘         │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## 📦 Installation

### Prerequisites
- Docker & Docker Compose
- (Optional) NVIDIA GPU with Docker runtime for acceleration

### Quick Start

1. **Clone and configure**
```bash
cd ai-service
cp .env.example .env
# Edit .env with your settings
```

2. **Start services**
```bash
docker-compose up -d
```

3. **Check health**
```bash
curl http://localhost:8080/health
```

---

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `AI_WORKERS` | 4 | Number of task workers |
| `AI_CONFIDENCE` | 0.5 | Detection confidence threshold |
| `MOTION_THRESHOLD` | 500 | Minimum contour area for motion |
| `ENABLE_GPU` | false | Enable NVIDIA GPU acceleration |
| `RTSP_ENABLED` | true | Enable RTSP stream processing |
| `BACKEND_URL` | http://gt-vision-backend:8000 | Django backend URL |
| `ADMIN_API_KEY` | - | API key for backend auth |

### GPU Support

For NVIDIA GPU:

1. Install [nvidia-docker](https://github.com/NVIDIA/nvidia-docker)
2. Uncomment GPU settings in `docker-compose.yml`
3. Set `ENABLE_GPU=true` in `.env`

---

## 📡 API Endpoints

### Task Mode (Queue-based)

#### POST `/detect`
Synchronous detection - waits for result
```bash
curl -X POST http://localhost:8080/detect \
  -H "Content-Type: application/json" \
  -d '{
    "camera_id": 1,
    "image_base64": "base64_encoded_image"
  }'
```

#### POST `/detect/async`
Asynchronous detection - returns task_id
```bash
curl -X POST http://localhost:8080/detect/async \
  -H "Content-Type: application/json" \
  -d '{
    "camera_id": 1,
    "image_base64": "base64_encoded_image"
  }'
```

#### GET `/result/{task_id}`
Get detection result
```bash
curl http://localhost:8080/result/1_12345678.90
```

### Webhook

#### POST `/lpr-webhook`
Receive external LPR camera webhooks
```bash
curl -X POST http://localhost:8080/lpr-webhook \
  -H "Content-Type: application/json" \
  -d '{
    "Plate": {"PlateNumber": "ABC1234"},
    "Channel": 1,
    "DeviceName": "Front Gate"
  }'
```

### Monitoring

#### GET `/health`
Health check with statistics
```bash
curl http://localhost:8080/health
```

#### GET `/stats/all`
Complete system statistics
```bash
curl http://localhost:8080/stats/all
```

#### GET `/metrics`
Prometheus metrics
```bash
curl http://localhost:8080/metrics
```

---

## 🎯 Processing Modes

### 1. Task Mode (Default)
- Images sent via API/Redis queue
- Ideal for single-shot detections
- Scalable with multiple workers

### 2. Stream Mode (RTSP)
- Continuous processing of RTSP streams
- **Motion Detection enabled** - only processes frames with movement
- Auto-reconnect on stream failure
- Configurable frame skipping for optimization

**Motion Detection saves ~60-80% CPU on static scenes!**

---

## 🧠 Motion Detection Optimization

The service includes intelligent motion detection:

```python
# Only runs heavy inference (YOLO + OCR) when motion detected
motion_detected = motion_detector.detect(frame)
if motion_detected:
    detections = vehicle_detector.detect(frame)
```

**Benefits:**
- Drastically reduces CPU/GPU usage on static scenes
- Extends hardware lifespan
- Perfect for edge devices (Jetson Nano, etc.)

**Configuration:**
- `MOTION_THRESHOLD`: Minimum contour area (default: 500)
- `MOTION_MIN_CHANGE`: Minimum frame change % (default: 0.02)

---

## 📊 Data Collection

### Auto-training Dataset
Every plate detected is automatically saved:
- Full frame: `/app/pending_training/{timestamp}.jpg`
- Metadata: `/app/pending_training/{timestamp}.txt`

### Plate Captures
Individual plate crops saved to:
- `/app/captures/plate_{camera_id}_{plate}_{timestamp}.jpg`

### Webhook JSONs
External LPR webhooks saved to:
- `/app/received_webhooks/{timestamp}_{plate}.json`

---

## 🔍 Integration with Django Backend

The service automatically:
1. Fetches camera list from backend
2. Sends detections/sightings back
3. Manages RTSP streams based on backend configuration

**Required Backend Endpoints:**
- `GET /api/v1/internal/cameras` - Get camera list
- `POST /api/v1/internal/sightings` - Send plate sighting

---

## 📈 Monitoring & Metrics

### Prometheus Metrics (`:9090/metrics`)
- `detections_processed_total` - Total detections
- `detection_processing_seconds` - Processing time histogram
- `detection_queue_size` - Current queue size
- `motion_detected` - Motion detection status
- `rtsp_streams_active` - Active RTSP streams

### Logs
Structured logging with levels:
- `DEBUG`: Detailed operation info
- `INFO`: Important events
- `WARNING`: Non-critical issues
- `ERROR`: Critical problems

---

## 🐛 Troubleshooting

### High CPU Usage
1. Enable motion detection (should be on by default)
2. Increase `RTSP_FRAME_SKIP` (process every Nth frame)
3. Reduce `AI_WORKERS` count
4. Consider GPU acceleration

### LPR Not Working
1. Check if `fast-plate-ocr` loaded: see startup logs
2. Verify model downloaded: check `/app/models/`
3. Test with clear, well-lit plate images
4. Adjust `AI_CONFIDENCE` threshold

### RTSP Stream Issues
1. Verify RTSP URL is accessible from container
2. Check camera supports the URL format
3. Monitor reconnection attempts in logs
4. Ensure network connectivity

### Redis Connection
1. Check `redis_cache` container is healthy: `docker-compose ps`
2. Verify Redis credentials in `.env`
3. Check Redis logs: `docker-compose logs redis_cache`

---

## 🚀 Performance Tips

### For Edge Devices (Jetson Nano, etc.)
```env
AI_WORKERS=2
MOTION_THRESHOLD=300
RTSP_FRAME_SKIP=10
ENABLE_GPU=true  # If available
```

### For High-Performance Servers
```env
AI_WORKERS=8
MOTION_THRESHOLD=500
RTSP_FRAME_SKIP=2
ENABLE_GPU=true
```

---

## 📝 License

GT-Vision AI Service - Proprietary

---

## 👥 Support

For issues and feature requests, contact the GT-Vision team.

---

**Built with ❤️ for efficient edge AI processing**
