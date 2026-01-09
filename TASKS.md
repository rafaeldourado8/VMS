# VMS Implementation Tasks

**Status**: 12 câmeras streaming ✅ | Resilience 🔄 | AI 50% | Recording ❌ | Security 40%

---

## 🛡️ PHASE 1: STREAMING RESILIENCE & LIMITS (CRITICAL - 2-3 days)

### Task 1.0: Stream Concurrency Limits (MVP Blocker)
- [x] Create `services/streaming/infrastructure/stream_limiter.py` ✅
- [x] Create `services/streaming/infrastructure/snapshot_cache.py` ✅
- [x] Create `frontend/src/hooks/useDynamicMosaic.ts` ✅
- [x] Edit `backend/apps/usuarios/models.py`
  - Add field: `plan` (free/pro/enterprise)
  - Add field: `max_concurrent_streams` (calculated from plan)
- [x] Edit `backend/apps/cameras/views.py`
  - Integrate StreamLimiter before returning stream_url
  - Return 429 if limit exceeded
- [x] Edit `frontend/src/pages/MosaicosPage.tsx` ✅
  - Use useDynamicMosaic hook
  - Check limit before opening stream
  - Show "Limite de X streams atingido" error
  - Tests created
- [x] Create `services/ai_detection/workers/snapshot_worker.py` ✅
  - Generate snapshots async (1 per 30s)
  - Publish to Redis via SnapshotCache
  - Tests created

### Task 1.1: Camera Auto-Reconnection
- [x] Edit `services/streaming/infrastructure/rtsp_client.py` ✅
  - Add retry loop: exponential backoff (5s → 10s → 30s → 60s)
  - Max retry: 10 attempts, then mark offline
  - Log reconnection attempts
- [x] Add health check: ping RTSP every 30s ✅
- [x] Metric: `vms_camera_reconnect_total{camera_id, status}` ✅
  - Tests created 

### Task 1.2: Frozen Stream Detection
- [x] Create `services/streaming/infrastructure/watchdog.py` ✅
  - Check frame timestamps every 15s
  - If no new frames for 30s → restart pipeline
  - Publish event: `stream.frozen` to RabbitMQ
- [x] Add to streaming service startup ✅
- [x] Metric: `vms_stream_frozen_total{camera_id}` ✅
  - Tests created

### Task 1.3: Protocol Failover (WebRTC → HLS)
- [ ] Edit `frontend/src/components/VideoPlayer.tsx`
  - Try WebRTC first (WHIPClient)
  - On error/timeout (5s): auto-switch to HLS
  - Show indicator: "Baixa Latência" / "Modo Compatível"
  - Retry WebRTC after 60s
- [ ] Add player event: `onProtocolSwitch`
- [ ] Metric: `vms_protocol_fallback_total{camera_id, from, to}`

### Task 1.4: Resilient Player
- [ ] Edit `frontend/src/hooks/useVideoPlayer.ts`
  - Detect stalled: `video.readyState < 3` for 5s
  - Auto-reload stream (max 3x/min)
  - Show "Reconectando..." overlay
  - After 3 failures: show error + manual retry button
- [ ] Persist player state in localStorage (volume, quality)

### Task 1.5: Pipeline Auto-Restart
- [ ] Edit `docker-compose.yml`
  - Add to all services: `restart: unless-stopped`
  - Add health checks:
    ```yaml
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:PORT/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    ```
- [ ] Create `/health` endpoint in all services
- [ ] Test: Kill service, verify auto-restart

### Task 1.6: Graceful Degradation
- [ ] Edit `frontend/src/components/CameraGrid.tsx`
  - If camera offline: show last frame + "Reconectando..."
  - If MediaMTX down: show "Servidor de streaming indisponível"
  - If all cameras down: show "Sistema em manutenção"
- [ ] Add retry button per camera
- [ ] Cache last frame in Redis (TTL: 5 min)

### Task 1.7: Basic Monitoring
- [ ] Create `services/streaming/infrastructure/metrics.py`
  - Metrics: `vms_streams_active`, `vms_stream_errors_total`, `vms_reconnect_duration_seconds`
- [ ] Add Prometheus to `docker-compose.yml`
- [ ] Create `config/prometheus/alerts.yml`
  - Alert: `CameraOffline` (no frames > 2 min)
  - Alert: `HighReconnectRate` (> 5/hour per camera)
  - Alert: `StreamingServiceDown`

**Acceptance**: Camera survives disconnect, player auto-recovers, frozen streams restart, alerts fire

---

## 🔥 PHASE 2: FIX AI + REKOGNITION TEST (1-2 days)

### Task 2.0: Rekognition Test Setup (Local → AWS)
- [ ] Edit `.env`
  - Add: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`
- [ ] Create `terraform/rekognition_test.tf`
  - S3 bucket for detection results
  - IAM role with Rekognition + S3 permissions
- [ ] Edit `services/ai_detection/infrastructure/providers/rekognition.py`
  - Add DetectText for license plates
  - Add DetectLabels for vehicle color/model
  - Save results to S3: `s3://vms-detections/{camera_id}/{timestamp}.json`
- [ ] Test: Local streaming → Rekognition → Frontend display + S3 storage
- [ ] Expected cost: ~$0.001/frame (test with 10 frames)

### Task 2.1: Fix Dependencies
- [x] Edit `services/ai_detection/requirements.txt`
  - Change: `typing-extensions>=4.8.0`
  - Change: `opencv-python-headless==4.8.1.78`
- [x] Rebuild: `docker-compose build --no-cache ai_worker_1 ai_worker_2`

### Task 2.2: Fix RabbitMQ Permissions
- [x] Edit `docker-compose.yml`
  - Add volume: `- ./config/rabbitmq/.erlang.cookie:/var/lib/rabbitmq/.erlang.cookie:ro`
- [x] Create `config/rabbitmq/.erlang.cookie` (chmod 400)
- [x] Restart: `docker-compose up -d rabbitmq_ai`

### Task 2.3: Frame Ingestion
- [x] Create `services/ai_detection/infrastructure/frame_extractor.py`
  - FFmpeg RTSP → JPEG (1 FPS)
  - Publish to RabbitMQ queue
- [x] Test: Verify frames in queue

### Task 2.4: Rekognition Adapter
- [x] Create `services/ai_detection/infrastructure/providers/rekognition.py`
  - Implement `DetectionProvider` protocol
  - DetectLabels + DetectFaces
  - Timeout: 5s, Retry: 3x
- [x] Test: Mock AWS call

### Task 2.5: Event Normalization
- [ ] Edit `services/ai_detection/domain/detection_result.py`
  - Normalize to `DetectionResult` schema
  - Add timestamp, camera_id, provider
- [ ] Persist to PostgreSQL
- [ ] Publish to RabbitMQ `detections` exchange

### Task 2.6: Cost Tracking
- [ ] Create `services/ai_detection/application/cost_tracker.py`
  - Track calls per camera
  - Calculate cost (DetectLabels: $0.001, DetectFaces: $0.001)
- [ ] Add metric: `vms_rekognition_cost_usd{camera_id}`

**Acceptance**: AI service starts, frames processed, results in DB + S3

---

## ☁️ PHASE 2.5: CLOUD INFRASTRUCTURE PLANNING (1 day)

### Task 2.5.1: Cloud Provider Analysis
- [ ] Create `docs/CLOUD_COMPARISON.md`
  - Compare: AWS, Azure, GCP, DigitalOcean, Hetzner
  - Metrics: cost, latency, features, support
  - Scenarios: 10 cameras, 50 cameras, 200 cameras

### Task 2.5.2: Cost Estimation
- [ ] Create `terraform/cost_calculator.xlsx`
  - Compute: EC2/ECS vs Fargate vs Lambda
  - Storage: S3 vs EBS vs EFS
  - Network: Data transfer, NAT Gateway
  - AI: Rekognition calls per month
  - Total: Barato ($50-100), Médio ($200-500), Caro ($1000+), Ideal

### Task 2.5.3: Architecture Decision
- [ ] Create `docs/CLOUD_ARCHITECTURE.md`
  - Chosen provider + justification
  - Services: Compute, Storage, Database, Cache, Queue
  - Regions: Primary + DR
  - Scaling strategy: Horizontal vs Vertical

**Acceptance**: Cloud provider chosen, cost estimated, architecture documented

---

## 🚀 PHASE 9: CLOUD DEPLOYMENT (5-7 days)
*Execute after Phase 8 (Tests)*

### Task 9.1: AWS Base Infrastructure
- [ ] Create `terraform/modules/vpc/main.tf`
  - VPC with public/private subnets
  - NAT Gateway, Internet Gateway
  - Security groups
- [ ] Create `terraform/modules/ecs/main.tf`
  - ECS Cluster
  - Task definitions: backend, streaming, ai_detection
  - Auto-scaling policies
- [ ] Create `terraform/modules/rds/main.tf`
  - PostgreSQL RDS (Multi-AZ for prod)
  - Read replicas
- [ ] Create `terraform/modules/elasticache/main.tf`
  - Redis cluster
- [ ] Create `terraform/modules/s3/main.tf`
  - Buckets: recordings, detections, backups
  - Lifecycle policies

### Task 9.2: Container Registry
- [ ] Create `terraform/ecr.tf`
  - ECR repositories for all services
- [ ] Create `.github/workflows/build-push.yml`
  - Build Docker images
  - Push to ECR
  - Tag: git commit SHA

### Task 9.3: Load Balancer & CDN
- [ ] Create `terraform/modules/alb/main.tf`
  - Application Load Balancer
  - Target groups: backend, streaming
  - Health checks
- [ ] Create `terraform/modules/cloudfront/main.tf`
  - CloudFront distribution for frontend
  - Origin: S3 bucket
  - Cache policies

### Task 9.4: Secrets & Config
- [ ] Create `terraform/modules/secrets/main.tf`
  - Secrets Manager: DB passwords, API keys
  - Parameter Store: config values
- [ ] Edit all services to read from Secrets Manager

### Task 9.5: Monitoring & Logging
- [ ] Create `terraform/modules/cloudwatch/main.tf`
  - Log groups for all services
  - Metrics: CPU, memory, requests
  - Alarms: high error rate, high latency
- [ ] Create `terraform/modules/sns/main.tf`
  - SNS topics for alerts
  - Email/Slack subscriptions

### Task 9.6: CI/CD Pipeline
- [ ] Create `.github/workflows/deploy-staging.yml`
  - Run tests
  - Build images
  - Deploy to staging ECS
- [ ] Create `.github/workflows/deploy-prod.yml`
  - Manual approval
  - Blue-green deployment
  - Rollback on failure

### Task 9.7: Backup & DR
- [ ] Create `terraform/modules/backup/main.tf`
  - RDS automated backups (7 days)
  - S3 cross-region replication
  - EBS snapshots
- [ ] Create disaster recovery runbook

### Task 9.8: Cost Optimization
- [ ] Enable AWS Cost Explorer
- [ ] Set up billing alerts
- [ ] Review: Reserved Instances, Savings Plans
- [ ] Implement: S3 Intelligent-Tiering

**Acceptance**: Full stack running on AWS, CI/CD working, monitoring active

---

## 💰 CLOUD COST COMPARISON (Preliminary)

### Scenario: 50 Cameras, 10 Users, 24/7 Operation

| Provider | Tier | Monthly Cost | Pros | Cons |
|----------|------|--------------|------|------|
| **AWS** | Barato | $150-250 | t3.medium, RDS t3.micro, S3 Standard | Limited scaling |
| **AWS** | Médio | $400-600 | t3.large, RDS t3.small, ElastiCache | Good balance |
| **AWS** | Caro | $1200-1800 | c5.xlarge, RDS r5.large, Multi-AZ | High availability |
| **AWS** | Ideal | $600-900 | Mix: Fargate + EC2 Spot, Aurora Serverless | Cost-optimized |
| **Azure** | Médio | $450-700 | Similar to AWS, better Windows support | Slightly more expensive |
| **GCP** | Médio | $380-550 | Cheaper compute, good AI services | Less mature VMS ecosystem |
| **DigitalOcean** | Barato | $100-180 | Simple, predictable pricing | Limited services, no Rekognition |
| **Hetzner** | Barato | $80-150 | Cheapest compute in EU | No managed AI, manual setup |

### Recommendation: **AWS Ideal Tier ($600-900/month)**
- ECS Fargate for services (auto-scaling)
- EC2 Spot for AI workers (70% cheaper)
- Aurora Serverless v2 (pay per use)
- S3 Intelligent-Tiering (auto cost optimization)
- Rekognition (only service with vehicle detection)

**Cost Breakdown**:
- Compute (ECS Fargate): $250
- Database (Aurora Serverless): $150
- Storage (S3 + EBS): $100
- Network (Data transfer): $80
- AI (Rekognition): $50 (with 90% optimization)
- Cache/Queue (ElastiCache + SQS): $70
- Monitoring (CloudWatch): $30
- **Total**: ~$730/month

---

## 💡 PHASE 3: AI COST OPTIMIZATION (1 day)

### Task 3.1: ROI Configuration (Região de Interesse)
- [x] `backend/apps/cameras/models.py` already has `roi_areas` JSONField ✅
- [ ] Verify format matches: `[{"x": 100, "y": 200, "width": 400, "height": 300}]`
- [ ] Create `frontend/src/components/ROIEditor.tsx`
  - Canvas overlay on video
  - Draw rectangles with mouse
  - Save to backend

### Task 3.2: ROI + Motion Trigger
- [ ] Edit `services/ai_detection/infrastructure/frame_extractor.py`
  - Crop to ROI before sending
  - Compare frames: skip if pixel diff < 3%
  - Only send if motion detected
- [ ] Config: `MOTION_THRESHOLD=0.03`, `AI_INTERVAL_SECONDS=10`
- [ ] Expected: 90-95% cost reduction

### Task 3.3: Cost Dashboard
- [ ] Create `backend/apps/analytics/views.py`
  - GET `/api/analytics/ai-cost`
- [ ] Add Grafana panel: cost per camera, frames skipped

**Acceptance**: ROI configured, motion skips 90%+ frames, cost < $1/day

---

## 📹 PHASE 4: RECORDING & PLAYBACK (3-5 days)

### Task 4.1: Storage Structure
- [ ] Create `services/recorder/storage.py`
  - Path: `/{camera_id}/{yyyy}/{mm}/{dd}/{hh}/segment_{timestamp}.mp4`
  - Retention config: 7/15/30 days
- [ ] Create storage directory: `/mnt/vms/recordings/`

### Task 4.2: Recorder Service
- [ ] Create `services/recorder/main.py`
  - FastAPI service
  - Endpoint: POST /record/start, /record/stop
- [ ] Create `services/recorder/ffmpeg_recorder.py`
  - Input: `rtsp://mediamtx:8554/camera/{id}`
  - Output: MP4 segments (1-5 min)
  - Filename: `{camera_id}_{timestamp}.mp4`
- [ ] Add to `docker-compose.yml`

### Task 4.3: Cleanup Job
- [ ] Create `services/recorder/cleanup.py`
  - Cron: daily at 2 AM
  - Delete files older than retention
- [ ] Add to `docker-compose.yml` as cron service

### Task 4.4: Playback API (Backend)
- [ ] Create `backend/apps/playback/` Django app
- [ ] Create `backend/domain/playback/recording.py`
  - Entity: Recording (camera_id, start, end, path)
- [ ] Create `backend/apps/playback/views.py`
  - GET `/api/playback/{camera_id}?start=ISO&end=ISO`
  - Return: MP4 URL or HLS playlist
- [ ] Create `backend/infrastructure/persistence/recording_repository.py`

### Task 4.5: Timeline UI
- [ ] Create `frontend/src/components/Timeline.tsx`
  - Canvas-based timeline
  - Show recording segments
  - Seek to timestamp
- [ ] Create `frontend/src/components/PlaybackPlayer.tsx`
  - Video.js player
  - Load MP4 from API
- [ ] Add to camera detail page

**Acceptance**: Record 5 min, playback works, timeline shows segments

---

## 🔐 PHASE 5: SECURITY (3-5 days)

### Task 5.1: JWT Generation
- [ ] Create `backend/infrastructure/auth/jwt_service.py`
  - Generate JWT with 1h expiry
  - Claims: `camera_id`, `tenant_id`, `permissions`
  - Secret from env: `JWT_SECRET`
- [ ] Add endpoint: POST `/api/auth/stream-token`

### Task 5.2: Redis Blacklist
- [ ] Create `backend/infrastructure/auth/blacklist.py`
  - Add token to Redis on revoke
  - Check blacklist on validation
- [ ] Add endpoint: POST `/api/auth/revoke`

### Task 5.3: Kong Rate Limiting
- [ ] Edit `kong/kong.yml`
  - Add plugin: `rate-limiting`
  - Config: 100 req/min per consumer
- [ ] Test: Exceed limit, verify 429

### Task 5.4: JWT Validation MediaMTX
- [ ] Edit `mediamtx.yml`
  - Add `authHTTPAddress: http://backend:8000/api/auth/validate-stream`
- [ ] Create `backend/apps/cameras/views.py`
  - POST `/api/auth/validate-stream`
  - Validate JWT, check camera_id claim
  - Return 200 or 401

### Task 5.5: RBAC Implementation
- [ ] Edit `backend/apps/usuarios/permissions.py`
  - Roles: `viewer`, `operator`, `admin`
  - Permissions: `view_stream`, `control_camera`, `manage_config`
- [ ] Apply to all endpoints with `@permission_required`

### Task 5.6: Audit Log
- [ ] Create `backend/apps/audit/models.py`
  - Fields: user, action, resource, timestamp, ip
- [ ] Create middleware: `backend/infrastructure/auth/audit_middleware.py`
  - Log all POST/PUT/DELETE requests
- [ ] Add to `MIDDLEWARE` in settings

### Task 5.7: AWS Secrets Manager
- [ ] Create `terraform/modules/secrets/main.tf`
  - Store: DB password, JWT secret, AWS keys
- [ ] Edit services to read from Secrets Manager
- [ ] Remove secrets from `.env`

### Task 5.8: TLS Internal
- [ ] Generate certs: `scripts/generate_certs.sh`
- [ ] Edit `docker-compose.yml`
  - Mount certs to all services
  - Update URLs to https://
- [ ] Test: Verify TLS handshake

**Acceptance**: JWT auth works, rate limit active, audit log captures actions

---

## 🔔 PHASE 6: EVENTS & ORCHESTRATION (2-3 days)

### Task 6.1: RabbitMQ Exchanges
- [ ] Create `config/rabbitmq/definitions.json`
  - Exchange: `detections` (topic)
  - Exchange: `alerts` (fanout)
  - Queue: `detections.processing`
  - Queue: `alerts.notifications`
- [ ] Edit `docker-compose.yml`
  - Mount definitions to RabbitMQ
  - Env: `RABBITMQ_DEFINITIONS=/etc/rabbitmq/definitions.json`

### Task 6.2: DLQ Configuration
- [ ] Edit `config/rabbitmq/definitions.json`
  - Queue: `detections.dlq`
  - Queue: `alerts.dlq`
  - Bind with `x-dead-letter-exchange`
- [ ] Set TTL: 24h on DLQ

### Task 6.3: Celery Consumer
- [ ] Create `backend/infrastructure/messaging/celery_consumer.py`
  - Task: `process_detection_event`
  - Consume from `detections.processing`
  - Persist to `detection_results` table
- [ ] Edit `backend/config/celery.py`
  - Register task
  - Set broker: RabbitMQ

### Task 6.4: Retry Logic
- [ ] Edit `backend/infrastructure/messaging/celery_consumer.py`
  - Add `@task(bind=True, max_retries=3)`
  - Exponential backoff: 2^retry seconds
- [ ] Test: Simulate failure, verify retries

### Task 6.5: WebSocket Push
- [ ] Create `backend/infrastructure/messaging/websocket.py`
  - Django Channels consumer
  - Subscribe to `detections` exchange
- [ ] Create `backend/apps/dashboard/consumers.py`
  - Push to WebSocket on new detection
- [ ] Edit `frontend/src/hooks/useDetections.ts`
  - Connect to WebSocket
  - Update state on message

**Acceptance**: Detection event → Celery → DB → WebSocket → Dashboard

---

## 📊 PHASE 7: OBSERVABILITY (2-3 days)

### Task 7.1: Prometheus Metrics
- [ ] Create `config/prometheus/prometheus.yml`
  - Scrape: streaming:8001, ai:8002, backend:8000
- [ ] Add to `docker-compose.yml`
- [ ] Create `services/streaming/infrastructure/metrics.py`
  - Metrics: `vms_streams_active`, `vms_webrtc_latency_ms`
- [ ] Create `services/ai_detection/infrastructure/metrics.py`
  - Metrics: `vms_rekognition_calls`, `vms_rekognition_cost_usd`
- [ ] Create `backend/infrastructure/metrics.py`
  - Metrics: `vms_api_requests`, `vms_storage_bytes`

### Task 7.2: Structured Logging
- [ ] Edit all services `main.py`
  - Use `structlog` or `python-json-logger`
  - Format: `{"service": "streaming", "level": "INFO", "message": "...", "trace_id": "...", "camera_id": "..."}`
- [ ] Add `trace_id` to all requests (middleware)

### Task 7.3: Alertmanager Rules
- [ ] Create `config/prometheus/alerts.yml`
  - Alert: `StreamOffline` (no frames > 60s)
  - Alert: `StorageCritical` (disk > 90%)
  - Alert: `AICostAnomaly` (daily cost > threshold)
- [ ] Add Alertmanager to `docker-compose.yml`
- [ ] Configure webhook to Slack/email

### Task 7.4: Grafana Dashboards
- [ ] Create `config/grafana/dashboards/vms.json`
  - Panel: Active streams per camera
  - Panel: WebRTC latency
  - Panel: AI cost per camera
  - Panel: Storage usage
- [ ] Add Grafana to `docker-compose.yml`
- [ ] Import dashboard

**Acceptance**: Metrics visible, logs structured, alerts firing, dashboard operational

---

## ⚡ PHASE 8: TESTS (3-5 days)

### Task 8.1: Streaming Tests
- [ ] Create `services/streaming/tests/test_resilience.py`
  - `test_camera_disconnect_reconnect`
  - `test_webrtc_fallback_to_hls`
  - `test_stream_recovery_after_mediamtx_restart`
- [ ] Create `services/streaming/tests/test_auth.py`
  - `test_jwt_expiry_rejection`
  - `test_invalid_token_rejection`

### Task 8.2: AI Tests
- [ ] Create `services/ai_detection/tests/test_providers.py`
  - `test_provider_interface_compliance`
  - `test_rekognition_timeout_handling`
  - `test_detection_false_positive_rate`
- [ ] Create `services/ai_detection/tests/test_cost.py`
  - `test_cost_tracking_accuracy`

### Task 8.3: Playback Tests
- [ ] Create `backend/tests/integration/test_playback.py`
  - `test_gap_in_recordings`
  - `test_playback_seek_accuracy`
  - `test_concurrent_playback_sessions`

**Acceptance**: All tests pass, coverage > 80%

---

## 📋 PRIORITY SUMMARY

**Current Focus**: PHASE 1 (Streaming Resilience & Limits) - 2-3 days

### What We Already Have (70% Complete):
- ✅ Camera model with ROI, AI settings, recording config
- ✅ StreamLimiter class (Redis-based)
- ✅ SnapshotCache class (Redis-based)
- ✅ useDynamicMosaic hook (React)
- ✅ User model with roles (admin/viewer)
- ✅ MediaMTX, Redis, RabbitMQ infrastructure
- ✅ Terraform base structure

### Critical Gaps (MVP Blockers):
- ❌ User.plan field (free/pro/enterprise)
- ❌ API enforcement (StreamLimiter integration)
- ❌ Frontend limit check before stream
- ❌ Snapshot async worker
- ❌ Mosaic page using dynamic hook
- ❌ Rekognition test with S3 storage
- ❌ Cloud provider decision

### Execution Order:
1. **Phase 1**: Streaming Resilience & Limits (2-3 days)
2. **Phase 2**: Fix AI + Rekognition Test (1-2 days)
3. **Phase 2.5**: Cloud Planning (1 day) ← NEW
4. **Phase 3**: AI Cost Optimization (1 day)
5. **Phase 4**: Recording & Playback (3-5 days)
6. **Phase 5**: Security (3-5 days)
7. **Phase 6**: Events & Orchestration (2-3 days)
8. **Phase 7**: Observability (2-3 days)
9. **Phase 8**: Tests (3-5 days)
10. **Phase 9**: Cloud Deployment (5-7 days) ← NEW

**Total Timeline**: 23-37 days (3-5 weeks)

**Cloud Strategy**:
- Phase 2: Test Rekognition only (local streaming)
- Phase 2.5: Decide cloud provider & architecture
- Phase 9: Full cloud deployment after all features tested locally
- Users depend on stable streaming
- 12 cameras working but fragile
- Must handle disconnects gracefully

**Next Steps**:
1. Phase 1: Streaming Resilience (CRITICAL)
2. Phase 2: Fix AI (complete detection pipeline)
3. Phase 3: AI Cost Optimization (reduce 90% costs)
4. Phase 4: Recording (core VMS feature)
5. Phase 5: Security (production requirement)
6. Phase 6-8: Events, Observability, Tests

**Estimated Timeline**:
- Minimum Viable: Phases 1-3 (4-6 days)
- Production Ready: Phases 1-5 (11-16 days)
- Enterprise Ready: All phases (18-26 days)
