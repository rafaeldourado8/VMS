# GT-Vision AI Service - Deployment Guide

## 🚀 Deployment Options

### Option 1: Standard Docker Deployment (Recommended)

#### Prerequisites
- Docker Engine 20.10+
- Docker Compose 2.0+
- 4GB RAM minimum (8GB recommended)
- 10GB free disk space

#### Steps

1. **Prepare environment**
```bash
cd ai-service
cp .env.example .env
nano .env  # Edit configuration
```

2. **Download YOLO model** (if not included)
```bash
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt
mv yolov8n.pt models/
```

3. **Start services**
```bash
docker-compose up -d
```

4. **Verify deployment**
```bash
docker-compose ps
docker-compose logs -f ai-service
curl http://localhost:8080/health
```

5. **Run tests**
```bash
python test_api.py
```

---

### Option 2: GPU-Accelerated Deployment (NVIDIA)

#### Prerequisites
- NVIDIA GPU (GTX 1060 or better)
- NVIDIA Driver 470+
- [nvidia-docker](https://github.com/NVIDIA/nvidia-docker) installed

#### Steps

1. **Install nvidia-docker**
```bash
# Ubuntu/Debian
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update
sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker
```

2. **Test GPU access**
```bash
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
```

3. **Update docker-compose.yml**
Uncomment GPU sections:
```yaml
ai-service:
  runtime: nvidia
  environment:
    - NVIDIA_VISIBLE_DEVICES=all
    - ENABLE_GPU=true
```

4. **Update .env**
```bash
ENABLE_GPU=true
```

5. **Deploy**
```bash
docker-compose up -d
```

---

### Option 3: Edge Device Deployment (Jetson Nano)

#### Specifications
- NVIDIA Jetson Nano 4GB
- Ubuntu 18.04 (JetPack 4.6+)
- Swap space configured (4GB recommended)

#### Optimizations for Jetson

1. **Update .env for edge**
```bash
AI_WORKERS=2
AI_BATCH_SIZE=4
MOTION_THRESHOLD=300
RTSP_FRAME_SKIP=10
ENABLE_GPU=true
```

2. **Configure swap**
```bash
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

3. **Optimize power mode**
```bash
sudo nvpmodel -m 0  # Max performance mode
sudo jetson_clocks   # Max clocks
```

4. **Build and deploy**
```bash
docker-compose build
docker-compose up -d
```

---

## 🔧 Configuration Profiles

### Profile: High-Performance Server
**Hardware**: 8-core CPU, 16GB RAM, RTX 3080
```env
AI_WORKERS=8
AI_BATCH_SIZE=16
MOTION_THRESHOLD=500
RTSP_FRAME_SKIP=2
ENABLE_GPU=true
```

### Profile: Standard Server
**Hardware**: 4-core CPU, 8GB RAM, GTX 1660
```env
AI_WORKERS=4
AI_BATCH_SIZE=8
MOTION_THRESHOLD=500
RTSP_FRAME_SKIP=5
ENABLE_GPU=true
```

### Profile: Edge Device
**Hardware**: Jetson Nano, 4GB RAM
```env
AI_WORKERS=2
AI_BATCH_SIZE=4
MOTION_THRESHOLD=300
RTSP_FRAME_SKIP=10
ENABLE_GPU=true
```

### Profile: CPU-Only
**Hardware**: 4-core CPU, 8GB RAM
```env
AI_WORKERS=3
AI_BATCH_SIZE=4
MOTION_THRESHOLD=400
RTSP_FRAME_SKIP=8
ENABLE_GPU=false
```

---

## 📊 Monitoring

### Health Check
```bash
curl http://localhost:8080/health | jq
```

### Live Logs
```bash
docker-compose logs -f ai-service
```

### Prometheus Metrics
```bash
curl http://localhost:8080/metrics
```

### Resource Usage
```bash
docker stats gtvision_ai
```

---

## 🔄 Updates

### Update to Latest Version
```bash
cd ai-service
git pull
docker-compose pull
docker-compose up -d
```

### Rebuild After Code Changes
```bash
docker-compose build --no-cache
docker-compose up -d
```

---

## 🐛 Troubleshooting

### Service won't start
```bash
# Check logs
docker-compose logs ai-service

# Check Redis
docker-compose logs redis_cache

# Verify network
docker network ls | grep gt-vision
```

### High memory usage
```bash
# Reduce workers
AI_WORKERS=2

# Reduce batch size
AI_BATCH_SIZE=4

# Enable motion detection optimization
MOTION_THRESHOLD=300
```

### GPU not detected
```bash
# Check NVIDIA runtime
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi

# Verify compose configuration
grep -A5 "runtime: nvidia" docker-compose.yml
```

### RTSP streams not working
```bash
# Test RTSP URL manually
ffprobe rtsp://camera-ip:554/stream

# Check logs for connection errors
docker-compose logs ai-service | grep RTSP

# Verify network access
docker-compose exec ai-service ping camera-ip
```

---

## 🔒 Security

### Production Deployment

1. **Change default ports**
```yaml
ports:
  - "8443:8000"  # Use non-standard ports
```

2. **Add authentication**
Configure reverse proxy (nginx/traefik) with SSL and auth

3. **Restrict Redis access**
```yaml
redis_cache:
  command: redis-server --requirepass your-secure-password
```

4. **Use secrets for API keys**
```bash
docker secret create admin_api_key /path/to/key
```

---

## 📈 Performance Tuning

### CPU Optimization
```env
AI_WORKERS=<num_cpu_cores>
RTSP_FRAME_SKIP=10
MOTION_THRESHOLD=300
```

### GPU Optimization
```env
ENABLE_GPU=true
AI_BATCH_SIZE=16
RTSP_FRAME_SKIP=2
```

### Memory Optimization
```env
AI_WORKERS=2
AI_BATCH_SIZE=4
```

### Network Optimization
```yaml
deploy:
  resources:
    limits:
      memory: 2G
```

---

## 🔄 Backup & Restore

### Backup Important Data
```bash
# Backup captures and training data
docker run --rm -v ai_captures:/data -v $(pwd):/backup \
  alpine tar czf /backup/captures_backup.tar.gz /data

# Backup configuration
cp .env .env.backup
cp docker-compose.yml docker-compose.yml.backup
```

### Restore Data
```bash
docker run --rm -v ai_captures:/data -v $(pwd):/backup \
  alpine tar xzf /backup/captures_backup.tar.gz -C /
```

---

## 📞 Support

For deployment issues:
1. Check logs: `docker-compose logs ai-service`
2. Run tests: `python test_api.py`
3. Check health: `curl http://localhost:8080/health`
4. Review documentation: `README.md`

---

**Deployment Guide v2.0**
