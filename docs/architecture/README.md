# VMS Architecture Documentation

Complete technical documentation for the VMS (Video Monitoring System) platform.

## 📚 Documentation Index

### 1. [OVERVIEW — COMPLETE ARCHITECTURE](./OVERVIEW%20—%20COMPLETE%20ARCHITECTURE.md)
Complete system architecture with all components, data flows, and technology stack.

**Contents:**
- System architecture diagram
- Component responsibilities
- Data flow examples (camera creation, live view, AI detection)
- Technology stack details
- Deployment configuration
- Security features
- Performance optimizations
- Monitoring & observability

### 2. [STREAMING — LIVE VIEW](./STREAMING%20—%20LIVE%20VIEW.md)
Detailed explanation of the live video streaming architecture.

**Contents:**
- Complete live view flow sequence
- HLS.js player configuration
- HAProxy routing logic
- MediaMTX on-demand streaming
- Stream provisioning flow
- HLS protocol details (playlists, segments)
- Performance characteristics and latency
- Error handling scenarios
- Multi-camera mosaic architecture

### 3. [RTSP — FROM CAMERA TO MediaMTX](./RTSP%20—%20FROM%20CAMERA%20TO%20MediaMTX.md)
Deep dive into RTSP protocol and camera-to-server communication.

**Contents:**
- Complete RTSP protocol flow (DESCRIBE, SETUP, PLAY, TEARDOWN)
- SDP (Session Description Protocol) details
- RTP packet structure and H.264 payload
- MediaMTX processing pipeline
- TCP vs UDP transport modes
- Bandwidth calculations
- Error scenarios and recovery
- Camera compatibility matrix
- Performance optimization strategies

### 4. [AI FLOW](./AI%20FLOW.md)
AI detection pipeline and machine learning integration.

**Contents:**
- Complete AI detection pipeline
- DDD architecture of AI service
- Frame extraction from HLS (1 FPS economic mode)
- YOLOv8 detection process
- ROI (Region of Interest) filtering
- License plate OCR with EasyOCR
- Database schema and storage
- RabbitMQ event publishing
- Performance optimizations
- Resource usage metrics

### 5. [API DESIGN](./API%20DESIGN.md)
Complete API reference for all services.

**Contents:**
- API architecture overview
- Authentication (JWT)
- Django Backend API (cameras, detections, dashboard, clips)
- Streaming Service API
- AI Detection Service API
- Error responses and status codes
- Rate limiting
- CORS configuration
- Pagination
- SDK examples (JavaScript, Python)
- Testing examples

## 🎯 Quick Start

### For Developers
1. Start with [OVERVIEW](./OVERVIEW%20—%20COMPLETE%20ARCHITECTURE.md) to understand the system
2. Review [API DESIGN](./API%20DESIGN.md) for integration
3. Check specific flows as needed

### For DevOps
1. Read [OVERVIEW](./OVERVIEW%20—%20COMPLETE%20ARCHITECTURE.md) for deployment
2. Review [STREAMING](./STREAMING%20—%20LIVE%20VIEW.md) for MediaMTX configuration
3. Check [RTSP](./RTSP%20—%20FROM%20CAMERA%20TO%20MediaMTX.md) for camera setup

### For Data Scientists
1. Focus on [AI FLOW](./AI%20FLOW.md) for ML pipeline
2. Review [API DESIGN](./API%20DESIGN.md) for AI endpoints
3. Check [OVERVIEW](./OVERVIEW%20—%20COMPLETE%20ARCHITECTURE.md) for data storage

## 🏗️ System Components

### Frontend
- **Technology**: React 18 + TypeScript + Vite
- **State Management**: Zustand + TanStack Query
- **UI**: Tailwind CSS + shadcn/ui
- **Video Player**: HLS.js

### Backend Services
- **Django Backend** (Port 8000): Main business logic, DDD architecture
- **Streaming Service** (Port 8001): FastAPI, stream lifecycle management
- **AI Detection Service** (Port 8002): FastAPI + YOLOv8, license plate detection

### Infrastructure
- **HAProxy** (Port 80): Load balancer and router
- **Kong Gateway** (Port 8000): API gateway with rate limiting
- **MediaMTX**: RTSP to HLS/WebRTC conversion
- **PostgreSQL** (Port 5432): Primary database
- **Redis** (Port 6379): Cache and sessions
- **RabbitMQ** (Port 5672): Message queue

## 📊 Key Metrics

### Performance
- **Streaming Latency**: 10-15 seconds (HLS)
- **AI Processing**: 1 FPS per camera (economic mode)
- **Max Concurrent Streams**: 4 cameras per mosaic
- **Max Users**: 4 concurrent users (MVP)

### Resource Usage
- **AI Detection**: 2 CPU, 3GB RAM
- **Streaming**: 1.5 CPU, 1GB RAM
- **Backend**: 0.5 CPU, 1GB RAM
- **MediaMTX**: 2.5 CPU, unlimited RAM

## 🔒 Security

- **Authentication**: JWT tokens with refresh
- **Rate Limiting**: Kong enforces API limits
- **CORS**: Configured for allowed origins
- **Network Isolation**: Services not exposed externally
- **Input Validation**: Pydantic (FastAPI) + DRF serializers (Django)

## 🚀 Deployment

### Development
```bash
docker-compose up -d
```

### Production
- Use environment-specific `.env` files
- Enable HTTPS via reverse proxy
- Configure proper CORS origins
- Set up monitoring and logging

## 📝 API Base URLs

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | `http://localhost` | React application |
| Backend API | `http://localhost/api` | Django REST API |
| Streaming API | `http://localhost/api/streaming` | Stream management |
| AI API | `http://localhost/api/ai` | AI detection |
| HLS Streams | `http://localhost/hls` | Video streaming |
| Admin Panel | `http://localhost/admin` | Django admin |
| HAProxy Stats | `http://localhost:8404/stats` | Load balancer stats |

## 🔍 Monitoring

- **HAProxy Stats**: http://localhost:8404/stats
- **Kong Metrics**: Prometheus plugin enabled
- **MediaMTX Metrics**: Port 9998
- **Health Checks**: All services have `/health` endpoints
- **Logs**: Centralized stdout logging

## 📖 Additional Resources

- [Main README](../../../README.md)
- [Docker Compose Configuration](../../../docker-compose.yml)
- [MediaMTX Configuration](../../../mediamtx.yml)
- [HAProxy Configuration](../../../haproxy/haproxy.cfg)
- [Kong Configuration](../../../kong/kong.yml)

## 🤝 Contributing

When updating architecture:
1. Update relevant diagram files
2. Keep code examples synchronized with actual implementation
3. Update this index if adding new documentation
4. Use Mermaid for all diagrams

## 📅 Last Updated

2026-01-08

---

**Note**: All diagrams use Mermaid syntax and can be rendered in GitHub, GitLab, or any Markdown viewer that supports Mermaid.
