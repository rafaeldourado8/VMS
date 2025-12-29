# GT-Vision AI Service - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Prerequisites Check
```bash
# Check Docker
docker --version  # Need 20.10+

# Check Docker Compose
docker-compose --version  # Need 2.0+

# Check available resources
free -h  # Need at least 4GB RAM
df -h    # Need at least 10GB disk space
```

### Step 2: Download and Configure
```bash
# Clone repository (or extract zip)
cd ai-service

# Copy environment template
cp .env.example .env

# Edit configuration (optional - defaults work fine)
nano .env
```

### Step 3: Start Services
```bash
# Start everything
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f ai-service
```

### Step 4: Verify Installation
```bash
# Health check
curl http://localhost:8080/health

# Should return:
# {
#   "status": "healthy",
#   "queue_size": 0,
#   "processed_total": 0,
#   ...
# }
```

### Step 5: Run Test Suite
```bash
# Install test dependencies (if not in container)
pip install requests opencv-python numpy

# Run tests
python test_api.py

# Expected output:
# ✅ All tests passed!
```

---

## 🎯 Your First Detection

### Option A: Using cURL (Simple)
```bash
# Create a test image
curl -o test_car.jpg https://example.com/car.jpg

# Convert to base64
IMAGE_B64=$(base64 -w 0 test_car.jpg)

# Detect
curl -X POST http://localhost:8080/detect \
  -H "Content-Type: application/json" \
  -d "{\"camera_id\": 1, \"image_base64\": \"$IMAGE_B64\"}"
```

### Option B: Using Python (Recommended)
```python
import requests
import base64

# Read image
with open('test_car.jpg', 'rb') as f:
    image_b64 = base64.b64encode(f.read()).decode('utf-8')

# Detect
response = requests.post(
    'http://localhost:8080/detect',
    json={'camera_id': 1, 'image_base64': image_b64}
)

# Print results
print(response.json())
```

---

## 📊 Monitor Your Service

### Check Health
```bash
# Full health status
curl http://localhost:8080/health | jq

# Statistics
curl http://localhost:8080/stats/all | jq
```

### View Logs
```bash
# Live logs
docker-compose logs -f ai-service

# Last 100 lines
docker-compose logs --tail 100 ai-service
```

### Resource Usage
```bash
# Container stats
docker stats gtvision_ai

# Disk usage
du -sh /var/lib/docker/volumes/ai_*
```

---

## 🔧 Common Configurations

### For Development
```bash
# .env
LOG_LEVEL=DEBUG
AI_WORKERS=2
RTSP_ENABLED=false
```

### For Production (Standard Server)
```bash
# .env
LOG_LEVEL=INFO
AI_WORKERS=4
RTSP_ENABLED=true
BACKEND_URL=http://your-backend:8000
ADMIN_API_KEY=your-secure-key
```

### For Edge Device (Jetson Nano)
```bash
# .env
LOG_LEVEL=INFO
AI_WORKERS=2
AI_BATCH_SIZE=4
MOTION_THRESHOLD=300
RTSP_FRAME_SKIP=10
ENABLE_GPU=true
```

---

## 🎥 Enable RTSP Streams

### 1. Configure Backend
Add cameras to your Django backend with RTSP URLs:
```json
{
  "id": 1,
  "name": "Front Gate",
  "rtsp_url": "rtsp://192.168.1.100:554/stream1",
  "active": true
}
```

### 2. Enable in AI Service
```bash
# .env
RTSP_ENABLED=true
BACKEND_URL=http://your-backend:8000
ADMIN_API_KEY=your-key
```

### 3. Restart Service
```bash
docker-compose restart ai-service
```

### 4. Verify Streams
```bash
# Check active streams
curl http://localhost:8080/stats/streams | jq

# Watch logs
docker-compose logs -f ai-service | grep RTSP
```

---

## 📡 Setup Webhook (External LPR Cameras)

### 1. Configure Your LPR Camera
Point webhook to:
```
http://your-server-ip:8080/lpr-webhook
```

### 2. Test Webhook
```bash
curl -X POST http://localhost:8080/lpr-webhook \
  -H "Content-Type: application/json" \
  -d '{
    "Plate": {"PlateNumber": "ABC1234"},
    "Channel": 1,
    "DeviceName": "Front Gate"
  }'
```

### 3. Check Saved Webhooks
```bash
docker-compose exec ai-service ls -lh /app/received_webhooks/
```

---

## 🐛 Quick Troubleshooting

### Service Won't Start
```bash
# Check logs
docker-compose logs ai-service

# Common issues:
# - Redis not ready: Wait 30 seconds
# - Port conflict: Change port in docker-compose.yml
# - Memory: Reduce AI_WORKERS
```

### High CPU Usage
```bash
# Check if motion detection is working
curl http://localhost:8080/stats/streams | jq

# Adjust motion sensitivity
# .env
MOTION_THRESHOLD=300
RTSP_FRAME_SKIP=10
```

### No Plates Detected
```bash
# Check LPR model loaded
docker-compose logs ai-service | grep "LPR model"

# Test with clear image
python test_api.py

# Adjust confidence
# .env
AI_CONFIDENCE=0.4
```

---

## 🔄 Update Service

### Pull Latest Version
```bash
cd ai-service
git pull  # or extract new zip
docker-compose pull
docker-compose up -d
```

### Rebuild After Changes
```bash
docker-compose build --no-cache
docker-compose up -d
```

---

## 📚 Next Steps

### Integration
- [ ] Connect to Django backend
- [ ] Setup RTSP cameras
- [ ] Configure webhooks
- [ ] Enable monitoring

### Optimization
- [ ] Tune motion detection
- [ ] Configure frame skipping
- [ ] Enable GPU (if available)
- [ ] Setup load balancing

### Documentation
- [ ] Read full README.md
- [ ] Check DEPLOYMENT.md for production
- [ ] Review EXAMPLES.md for code samples
- [ ] Study CHANGELOG.md for features

---

## 💡 Tips

### Performance
- Start with defaults, then tune based on your needs
- Motion detection saves 60-80% CPU - keep it enabled
- Use frame skipping on high-res streams
- Monitor with Prometheus for optimization

### Reliability
- Always use Docker volumes for data persistence
- Setup health check monitoring
- Configure auto-restart policies
- Keep logs for debugging

### Security
- Change default ports in production
- Use strong API keys
- Setup reverse proxy with SSL
- Restrict network access

---

## 🆘 Getting Help

### Check Documentation
1. README.md - Complete overview
2. DEPLOYMENT.md - Deployment guide
3. EXAMPLES.md - Code examples
4. This file - Quick start

### Debug Steps
1. Check logs: `docker-compose logs ai-service`
2. Test health: `curl http://localhost:8080/health`
3. Run tests: `python test_api.py`
4. Check resources: `docker stats`

### Common Commands
```bash
# Restart service
docker-compose restart ai-service

# View logs
docker-compose logs -f ai-service

# Check health
curl http://localhost:8080/health

# Run tests
python test_api.py

# Monitor resources
docker stats gtvision_ai
```

---

**You're all set! 🎉**

Your AI service is now detecting vehicles and recognizing license plates!

For advanced configuration and optimization, check the other documentation files.
